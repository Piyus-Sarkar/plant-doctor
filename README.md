# 🌿 The Plant Doctor: AI-Powered Botanical Diagnostics

# The Live Website Link: 
https://piyus-plant-doctor.streamlit.app/

## 📌 Project Overview
The Plant Doctor is a stateful, full-stack web application designed to diagnose plant health issues using advanced multimodal AI. Users can upload images of their houseplants, and the system instantly identifies the species, diagnoses cellular distress (e.g., chlorosis, necrosis), calculates a quantitative Vitality Score, and generates an interactive care plan.

This project was built as a Capstone Submission for the IIT Roorkee New Age Software Engineering certification.

## 🏗️ System Architecture
This application is decoupled into a high-performance backend API and a dynamic frontend dashboard, communicating via RESTful endpoints.

* **Frontend:** Streamlit (Python) - Handles complex state management, session memory, and UI rendering.
* **Backend:** FastAPI (Python) - High-performance asynchronous API for routing and business logic.
* **Database:** SQLite & SQLAlchemy (ORM) - Relational database maintaining a longitudinal medical history of plants, photos, and diagnoses.
* **AI Engine:** Google Gemini 2.5 Flash Vision API - Processes raw image bytes and system prompts to generate structured JSON botanical analysis.
* **Vector Engine:** Google text-embedding-004 - Generates 768-dimensional mathematical arrays for semantic searching.

## 🚀 Key Engineering Features
1. **Multimodal Diagnostics:** Analyzes physical plant photos using Google's latest Vision models.
2. **Live Microclimate Context:** Injects live satellite weather data (Open-Meteo API) based on the user's city so the AI understands environmental stressors before diagnosing.
3. **Semantic Vector Search:** Computes native cosine similarity against vectorized historical case logs, allowing users to search their database using natural conceptual phrases rather than exact keywords.
4. **Stateful Medical History & CRUD:** Full database integration tracks plant recovery over time. Features cascading relational deletion to safely erase specific visits without locking the database.
5. **Interactive Action Plans:** Generates dynamically rendered, checklist-based treatment plans and downloadable text prescriptions.

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
uvicorn main:app --reload

Terminal 2 (The Frontend Dashboard):
streamlit run app.py
