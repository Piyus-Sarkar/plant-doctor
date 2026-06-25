import os
import json
from pathlib import Path
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv

current_directory = Path(__file__).resolve().parent
load_dotenv(dotenv_path=current_directory / ".env")

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise KeyError("GEMINI_API_KEY environment variable not found.")

genai.configure(api_key=api_key)

# Change the function definition to accept environment_data
def diagnose_plant_with_vision(image_path: str, previous_diagnosis: str = None, environment_data: str = None):
    try:
        img = Image.open(image_path)
        
        model = genai.GenerativeModel(
            'gemini-2.5-flash',
            generation_config={"response_mime_type": "application/json"}
        )
        
        prompt = (
            "You are a master botanist. Analyze this plant image. "
            "You MUST return a raw JSON object with exactly these 5 keys: "
            "1. 'species': The name of the plant. "
            "2. 'category': ONE word [Water, Light, Pest, Nutrient, Disease, Healthy]. "
            "3. 'description': A 2-sentence medical diagnosis. "
            "4. 'health_score': An integer from 0 to 100 representing the plant's vitality. "
            "5. 'tasks': A Python list containing exactly 3 short, actionable care steps. "
        )
        
        # --- NEW: INJECT LIVE WEATHER CONTEXT ---
        if environment_data:
            prompt += f"\n\nENVIRONMENTAL CONTEXT: The plant is currently located in {environment_data}. Consider this live weather data in your diagnosis and care plan."
            
        if previous_diagnosis:
            prompt += f"\n\nMEDICAL HISTORY: Last week's diagnosis was: '{previous_diagnosis}'."
            
        response = model.generate_content([prompt, img])
        return json.loads(response.text)
        
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