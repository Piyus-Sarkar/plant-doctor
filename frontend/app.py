import streamlit as st
import requests
import time 

st.set_page_config(page_title="Plant Doctor", page_icon="🌿", layout="centered")
st.title("🌿 The Plant Doctor")

tab1, tab2 = st.tabs(["🩺 Diagnose Plant", "🪴 My Plants Dashboard"])

# --- TAB 1: THE CLINIC ---
with tab1:
    st.write("Upload a photo of your sick houseplant, and our AI will diagnose the cellular distress and prescribe a fix!")
    
    # 1. The new City Input for Weather Context
    city_input = st.text_input("Enter your city for live weather context:", "Kolkata")
    
    # 2. The File Uploader (Notice we added a unique 'key' to prevent ID errors!)
    uploaded_file = st.file_uploader("Choose a clear photo of the plant...", type=["jpg", "jpeg", "png"], key="plant_uploader")

    if uploaded_file is not None:
        # Clear old memory if a new file is uploaded
        if "last_file" not in st.session_state or st.session_state["last_file"] != uploaded_file.name:
            st.session_state.pop("current_diagnosis", None)
            st.session_state["last_file"] = uploaded_file.name

        st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
        
        # 3. The Submit Button
        if st.button("Diagnose Plant", type="primary"):
            with st.spinner("Analyzing botanical symptoms and fetching live satellite weather..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                form_data = {"city": city_input} # Sending the city to FastAPI
                
                try:
                    response = requests.post("https://plant-doctor-buxp.onrender.com/upload-photo/", files=files, data=form_data)
                    if response.status_code == 200:
                        st.session_state["current_diagnosis"] = response.json()
                    else:
                        st.error(f"Server Error: {response.status_code}")
                except Exception as e:
                    st.error(f"CRITICAL SYSTEM ERROR: {str(e)}")

        # 4. Render the UI from Memory
        if "current_diagnosis" in st.session_state:
            result = st.session_state["current_diagnosis"]
            
            # --- NEW: Catch the AI Error explicitly ---
            if result.get("message") == "AI Error":
                st.error(f"⚠️ AI System Error: {result.get('diagnosis')}")
            else:
                # Normal successful display
                st.success("Diagnosis Complete!")
                
                data = result.get("diagnosis_data", {})
                
                st.markdown(f"### 🪴 Species: {data.get('species', 'Unknown')}")
            
            # Vitality Score
            score = data.get('health_score', 0)
            st.metric(label="Vitality Score", value=f"{score}%")
            st.progress(score / 100.0)
            
            # Weather & Diagnosis
            st.info(f"🌤️ **Live Context Used:** {result.get('weather_context', 'Unknown')}")
            st.info(f"**Diagnosis ({data.get('category', 'General')}):** {data.get('description', '')}")
            
            # Interactive Checklist
            st.markdown("### 📋 Action Plan")
            for index, task in enumerate(data.get('tasks', [])):
                st.checkbox(task, key=f"task_{index}")

            # 5. Downloadable Prescription
            st.markdown("---")
            report_text = (
                f"🪴 PATIENT: {data.get('species', 'Unknown')}\n"
                f"📊 VITALITY SCORE: {score}%\n"
                f"🌤️ WEATHER CONTEXT: {result.get('weather_context', 'Unknown')}\n"
                f"🩺 DIAGNOSIS ({data.get('category', 'General')}): {data.get('description', '')}\n\n"
                f"📋 ACTION PLAN:\n"
            )
            for task in data.get('tasks', []):
                report_text += f"- {task}\n"
                
            st.download_button(
                label="📄 Download Official Care Plan",
                data=report_text,
                file_name=f"{data.get('species', 'Plant').replace(' ', '_')}_Prescription.txt",
                mime="text/plain",
                type="secondary"
            )

# --- TAB 2: THE DASHBOARD ---
with tab2:
    st.header("🪴 Patient Medical History")
    st.write("Review the complete longitudinal recovery records of your registered plants.")

    # REMOVED the "st.button" wrapper! The dashboard now loads automatically, fixing the bug.
    try:
        response = requests.get("https://plant-doctor-buxp.onrender.com/plants/")
        if response.status_code == 200:
            plants = response.json()

            if not plants:
                st.warning("No plants in the database yet! Go to the 'Diagnose Plant' tab to add one.")

            for plant in plants:
                with st.container(border=True):
                    # The confusing plant-level delete button is gone.
                    st.subheader(f"Patient ID: #{plant['plant_id']} - {plant['species']}")
                    st.markdown("### 📋 Complete Consultation Timeline")

                    for index, record in enumerate(plant["history"]):
                        is_latest = (index == 0)
                        expander_title = f"{'✨ LATEST' if is_latest else '🕒 Past'} CONSULT: {record['date']} ({record['category']})"

                        with st.expander(expander_title, expanded=is_latest):
                            col1, col2 = st.columns([1, 2])
                            with col1:
                                image_url = f"https://plant-doctor-buxp.onrender.com/{record['photo_path']}"
                                st.image(image_url, caption=f"Photo from {record['date']}", use_container_width=True)

                                # --- NEW: INDIVIDUAL RECORD DELETE BUTTON ---
                                if st.button("🗑️ Delete this Record", key=f"del_rec_{record['id']}", help="Erase this specific visit"):
                                    try:
                                        res = requests.delete(f"https://plant-doctor-buxp.onrender.com/diagnoses/{record['id']}")
                                        if res.status_code == 200:
                                            st.success("Record erased! Refreshing...")
                                            time.sleep(0.5)
                                            st.rerun()
                                        else:
                                            st.error(f"Deletion failed: {res.json().get('detail')}")
                                    except Exception as e:
                                        st.error("Deletion connection failed.")

                            with col2:
                                st.write(record['description'])
        else:
            st.error("Failed to load dashboard data.")
    except Exception as e:
        st.error(f"The TRUE error is: {str(e)}")

    # --- SEMANTIC SEARCH SECTOR ---
    st.markdown("---")
    st.subheader("🔍 Conceptual Case-File Search")
    st.write("Search historical diagnostic logs using natural conceptual phrases.")

    search_query = st.text_input("Enter search phrase:", placeholder="Type a symptom concept...")

    if st.button("Execute Vector Search", type="primary"):
        if search_query:
            with st.spinner("Analyzing case files..."):
                try:
                    response = requests.get("https://plant-doctor-buxp.onrender.com/diagnoses/search/", params={"query": search_query})

                    if response.status_code == 200:
                        matches = response.json()

                        if not matches:
                            st.warning("No matching historical case logs found.")

                        for match in matches:
                            with st.container(border=True):
                                col1, col2 = st.columns([1, 2])
                                with col1:
                                    if match["photo_path"]:
                                        search_image_url = f"https://plant-doctor-buxp.onrender.com/{match['photo_path']}"
                                        st.image(search_image_url, use_container_width=True)
                                with col2:
                                    st.markdown(f"#### {match['species']} (Record #{match['diagnosis_id']})")
                                    st.metric(label="Match Confidence", value=f"{match['match_accuracy']}%")
                                    st.write(f"**Historical Diagnostic Entry:** {match['description']}")
                    else:
                        st.error("Search query execution failed at the backend server.")
                except Exception as error:
                    st.error(f"Search pipeline connection failure: {str(error)}")
        else:
            st.warning("Please input a valid conceptual search phrase first.")