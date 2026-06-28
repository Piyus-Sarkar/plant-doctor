import os
import json
from pathlib import Path
from PIL import Image
from dotenv import load_dotenv
import google.generativeai as genai

# --- NEW: LANGGRAPH IMPORTS ---
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END

# Load environment variables
current_directory = Path(__file__).resolve().parent
load_dotenv(dotenv_path=current_directory / ".env")

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise KeyError("GEMINI_API_KEY environment variable not found.")

genai.configure(api_key=api_key)

# ==========================================
# 1. DEFINE THE AI "BRAIN STATE" (MEMORY)
# ==========================================
class AgentState(TypedDict):
    image_path: str
    previous_image_path: Optional[str]
    previous_diagnosis: Optional[str]
    environment_data: Optional[str]
    triage_decision: str
    triage_message: str
    final_result: dict

# ==========================================
# 2. AGENT 1: THE TRIAGE NURSE
# ==========================================
def triage_agent(state: AgentState):
    """Examines the photo to ensure it is valid before wasting the Doctor's time."""
    current_img = Image.open(state["image_path"])
    model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})
    
    prompt = (
        "You are the Triage Nurse for a plant clinic. "
        "Analyze this image. Your goal is to collect essential care data BEFORE the doctor diagnoses. "
        "Return a raw JSON object with exactly two keys: 'decision' and 'message'. "
        "1. If image is blurry/not a plant: decision='Reject', message='Explain why'. "
        "2. If it IS a clear plant: decision='Clarify', message='Ask 2 specific, mandatory questions: How often do you water this, and how much sunlight does it get?'. "
        "3. Only use 'Proceed' if you already have the answers to those two questions in the context."
    )
    
    try:
        response = model.generate_content([prompt, current_img])
        res_json = json.loads(response.text)
        return {"triage_decision": res_json.get("decision", "Proceed"), "triage_message": res_json.get("message", "")}
    except Exception as e:
        # If the API glitches, default to proceeding so the app doesn't crash
        return {"triage_decision": "Proceed", "triage_message": ""}

# ==========================================
# 3. AGENT 2: THE PLANT DOCTOR
# ==========================================
def doctor_agent(state: AgentState):
    """The original Phase 1 diagnosis engine."""
    current_img = Image.open(state["image_path"])
    model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})
    
    prompt = (
        "You are a master botanist. Analyze the plant image(s) provided. "
        "You MUST return a raw JSON object with exactly these 5 keys: "
        "1. 'species': The name of the plant. "
        "2. 'category': ONE word [Water, Light, Pest, Nutrient, Disease, Healthy]. "
        "3. 'description': A 2-sentence medical diagnosis. If two images are provided, explicitly state if the plant is recovering or degrading. "
        "4. 'health_score': An integer from 0 to 100. "
        "5. 'tasks': A Python list containing exactly 3 short, actionable care steps. "
    )
    
    if state.get("environment_data"):
        prompt += f"\n\nENVIRONMENTAL CONTEXT: The plant is in {state['environment_data']}."
        
    if state.get("previous_diagnosis"):
        prompt += f"\n\nMEDICAL HISTORY: The previous diagnosis was: '{state['previous_diagnosis']}'."

    payload = [prompt]
    
    if state.get("previous_image_path") and os.path.exists(state["previous_image_path"]):
        prompt += "\n\nVISUAL HISTORY: Image 1 is the PAST. Image 2 is TODAY. Compare them!"
        old_img = Image.open(state["previous_image_path"])
        payload.extend([old_img, current_img]) 
    else:
        payload.append(current_img)
        
    try:
        response = model.generate_content(payload)
        return {"final_result": json.loads(response.text)}
    except Exception as e:
        return {"final_result": {"error": str(e)}}

# ==========================================
# 4. THE INTERRUPTION HANDLER
# ==========================================
def interruption_agent(state: AgentState):
    """Formats rejections/questions into a safe JSON so the frontend doesn't crash."""
    decision = state["triage_decision"]
    message = state["triage_message"]
    
    tasks = ["Reply with more details"] if decision.lower() == "clarify" else ["Take a clearer photo", "Make sure it is a plant", "Upload again"]
    
    # We fake a diagnosis to safely send the message to the dashboard!
    safe_json = {
        "species": "Pending Clarification",
        "category": "Triage",
        "description": f"AI Triage ({decision.upper()}): {message}",
        "health_score": 0,
        "tasks": tasks
    }
    return {"final_result": safe_json}

# ==========================================
# 5. LANGGRAPH ROUTING LOGIC
# ==========================================
def route_triage(state: AgentState):
    """The brain pathing: Decide whether to go to the Doctor or Interrupt."""
    if state["triage_decision"].lower() == "proceed":
        return "doctor"
    return "interruption"

# Build the Graph Workflow
workflow = StateGraph(AgentState)
workflow.add_node("triage", triage_agent)
workflow.add_node("doctor", doctor_agent)
workflow.add_node("interruption", interruption_agent)

workflow.set_entry_point("triage")
workflow.add_conditional_edges("triage", route_triage, {"doctor": "doctor", "interruption": "interruption"})
workflow.add_edge("doctor", END)
workflow.add_edge("interruption", END)

# Compile the Agentic Engine
ai_app = workflow.compile()

# ==========================================
# 6. THE MAIN FASTAPI EXPORT
# ==========================================
def diagnose_plant_with_vision(image_path: str, previous_image_path: str = None, previous_diagnosis: str = None, environment_data: str = None, skip_triage: bool = False):
    try:
        inputs = {
            "image_path": image_path,
            "previous_image_path": previous_image_path,
            "previous_diagnosis": previous_diagnosis,
            "environment_data": environment_data
        }
        
        # THE BYPASS: If the user answered the question, send them straight to the Doctor!
        if skip_triage:
            result = doctor_agent(inputs)
            return result["final_result"]
            
        # Normal Flow: Start at the Triage Nurse
        result = ai_app.invoke(inputs)
        return result["final_result"]
    except Exception as e:
        return {"error": str(e)}

def generate_text_embedding(text: str):
    """Converts a string of text into a vector embedding array using Google AI."""
    try:
        result = genai.embed_content(
            model="models/text-embedding-004",
            contents=text,
            task_type="retrieval_document"
        )
        return result['embedding']
    except Exception as e:
        print(f"Failed to generate vector embedding: {e}")
        return None