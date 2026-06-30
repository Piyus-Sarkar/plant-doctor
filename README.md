# 🌿 The Plant Doctor: AI-Powered Botanical Diagnostics

# The Live Website Link: 
https://piyus-plant-doctor.streamlit.app/

## 📌 Project Overview
The Plant Doctor is a secure, stateful, full-stack web application designed to diagnose plant health issues using advanced multimodal AI. Users can create secure accounts to upload images of their houseplants, and the system uses an Agentic AI workflow to first triage the image quality, and then diagnose cellular distress, calculate a quantitative Vitality Score, and generate an interactive care plan.

This project was built as a Capstone Submission for the IIT Roorkee New Age Software Engineering certification.

## 🏗️ System Architecture
This application is decoupled into a high-performance backend API and a dynamic frontend dashboard, communicating via RESTful endpoints.

* **Frontend:** Streamlit (Python) - Handles complex state management, session memory, and UI rendering.
* **Backend:** FastAPI (Python) - High-performance asynchronous API for routing and business logic.
* **Agentic Workflow:** LangGraph - Implements a multi-agent StateGraph (Triage Nurse -> Plant Doctor) to handle dynamic user interruptions and data validation.
* **Security Layer:** Bcrypt & PyJWT - Handles cryptographic password hashing, JWT access tokens, and strict multi-user data isolation.
* **Database:** SQLite & SQLAlchemy (ORM) - Relational database maintaining an isolated, longitudinal medical history of plants for each authenticated user.
* **AI Engine:** Google Gemini 2.5 Flash Vision API - Processes raw image bytes and system prompts to generate structured JSON botanical analysis.
* **Vector Engine:** Google text-embedding-004 - Generates 768-dimensional mathematical arrays for semantic searching.

## 🚀 Key Engineering Features
1. **Agentic AI Triage (LangGraph):** Employs a Human-in-the-Loop workflow. A "Triage Agent" intercepts uploads, rejects non-plant/blurry images, and asks clarifying questions (e.g., watering habits) before routing the context to the Doctor Agent.
2. **Longitudinal Visual History:** The AI automatically pulls the user's previous plant photo from the database and runs a 2-image multimodal comparison to explicitly track recovery or degradation over time.
3. **Secure Multi-User Architecture:** Features JWT-based authentication and Bcrypt password hashing. Database queries are strictly scoped to the owner_id, ensuring complete data privacy and preventing cross-user data bleeding.
4. **Live Microclimate Context:** Injects live satellite weather data (Open-Meteo API) based on the user's city so the AI understands environmental stressors before diagnosing.
5. **Semantic Vector Search:** Computes native cosine similarity against vectorized historical case logs (Google text-embedding-004), allowing users to search their database using natural conceptual phrases rather than exact keywords.
6. **"Lazy" Database Writing:** Optimized backend architecture ensures that temporary files and interrupted triage sessions are cleared from memory and never corrupt the SQL database until a final medical diagnosis is reached.
7. **Interactive Action Plans:** Generates dynamically rendered, checklist-based treatment plans and downloadable text prescriptions.

## 💻 Local Installation & Setup

**1. Clone the repository**
git clone [https://github.com/Piyus-Sarkar/plant-doctor.git]
cd plant-doctor

**2.Set up the virtual environment**
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

**3. Install dependencies**
pip install -r requirements.txt

**4.Configure Environment Variables**
Create a .env file in the root directory and add your Google AI Studio key:
GEMINI_API_KEY=your_api_key_here

**5. Launch the Application (Requires Two Terminals)**

Terminal 1 (The Backend API):
cd backend
uvicorn main:app --reload

Terminal 2 (The Frontend Dashboard):
cd frontend
streamlit run app.py
