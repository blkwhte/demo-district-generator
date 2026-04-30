import streamlit as st
import os
import shutil
import datetime  # <-- Added to support the date picker
from generator_core import DEFAULTS, run_generation

st.set_page_config(page_title="Clever Demo Generator", page_icon="🏫")
st.title("🏫 Clever Demo District Generator")
st.markdown("Generate realistic, privacy-safe school datasets.")

# --- UI & CONFIGURATION ---
with st.sidebar:
    st.header("Configuration")
    config = DEFAULTS.copy()
    config["NUM_DISTRICTS"] = st.number_input("Number of Districts", min_value=1, value=DEFAULTS["NUM_DISTRICTS"])
    config["SCHOOLS_PER_DISTRICT"] = st.number_input("Schools per District", min_value=1, value=DEFAULTS["SCHOOLS_PER_DISTRICT"])
    config["ID_MODE"] = st.selectbox("ID Mode", ["alphanumeric", "sequential"], index=0)
    config["OUTPUT_SCHEMA"] = st.selectbox("Schema", ["standard", "anyschool", "both"], index=0)

    # --- NEW ATTENDANCE SECTION ---
    st.markdown("---")
    st.header("Attendance Data")
    config["DO_ATTENDANCE"] = st.checkbox("Generate Attendance Data", value=DEFAULTS.get("DO_ATTENDANCE", False))
    
    if config["DO_ATTENDANCE"]:
        # Show inputs if checked, and save directly to the config dict
        config["ATT_START_DATE"] = st.date_input("Start Date", value=datetime.date(2025, 9, 1)).strftime("%Y-%m-%d")
        config["ATT_DAYS"] = st.number_input("Number of Days", min_value=1, max_value=180, value=DEFAULTS.get("ATT_DAYS", 5))
        config["ATT_MODE"] = st.selectbox("Attendance Mode", options=["Section", "Daily"], index=0)
    else:
        # Fallback config so the generator core doesn't break if unchecked
        config["ATT_START_DATE"] = "2025-09-01"
        config["ATT_DAYS"] = 5
        config["ATT_MODE"] = "Section"

col1, col2 = st.columns(2)
with col1:
    config["TEACHERS_PER_SCHOOL"] = st.text_input("Teachers per School (Range)", value=DEFAULTS["TEACHERS_PER_SCHOOL"])
    config["STUDENTS_PER_SECTION"] = st.text_input("Students per Section (Range)", value=DEFAULTS["STUDENTS_PER_SECTION"])
    config["SECTIONS_PER_TEACHER_TERM"] = st.number_input("Sections per Teacher (Term)", min_value=1, value=DEFAULTS["SECTIONS_PER_TEACHER_TERM"])

with col2:
    config["SCHOOL_START_YEAR"] = st.text_input("Start Year (YYYY)", value=DEFAULTS["SCHOOL_START_YEAR"])
    config["NUM_TERMS"] = st.selectbox("Terms per Year", [2, 3, 4], index=0)
    config["INCLUDE_SUMMER"] = st.checkbox("Include Summer Session?", value=DEFAULTS["INCLUDE_SUMMER"])

with st.expander("Demographics Probabilities"):
    config["PROB_FRL"] = st.slider("Free/Reduced Lunch", 0.0, 1.0, DEFAULTS["PROB_FRL"])
    config["PROB_IEP"] = st.slider("IEP", 0.0, 1.0, DEFAULTS["PROB_IEP"])
    config["PROB_ELL"] = st.slider("ELL", 0.0, 1.0, DEFAULTS["PROB_ELL"])
    config["PROB_504"] = st.slider("504 Plan", 0.0, 1.0, DEFAULTS["PROB_504"])
    config["PROB_GIFTED"] = st.slider("Gifted", 0.0, 1.0, DEFAULTS["PROB_GIFTED"])
    config["PROB_DISABILITY"] = st.slider("Disability", 0.0, 1.0, DEFAULTS["PROB_DISABILITY"])

with st.expander("Advanced Settings"):
    config["EMAIL_DOMAIN"] = st.text_input("Custom Email Domain", value=DEFAULTS["EMAIL_DOMAIN"])
    config["USERNAME_FMT"] = st.selectbox("Username Format", ["first.last", "f.last", "f_last", "flast"], index=0)
    config["DO_CONTACTS"] = st.checkbox("Contacts", value=DEFAULTS["DO_CONTACTS"])
    config["DO_EXTENSIONS"] = st.checkbox("Extensions", value=DEFAULTS["DO_EXTENSIONS"])

# --- EXECUTION ---
if st.button("Generate Data", type="primary"):
    base_output_dir = 'district_data_output'
    if os.path.exists(base_output_dir): shutil.rmtree(base_output_dir)
    
    progress_bar = st.progress(0)
    status_text = st.empty()

    # Define how the core updates Streamlit's UI
    def update_status(msg): status_text.text(msg)
    def update_progress(val): progress_bar.progress(val)

    # Trigger the Brain
    run_generation(config, base_output_dir, status_callback=update_status, progress_callback=update_progress)

    status_text.success("Generation Complete! Creating Archive...")
    shutil.make_archive(base_output_dir, 'zip', base_output_dir)
    
    with open(f"{base_output_dir}.zip", "rb") as fp:
        st.download_button(label="Download Data (ZIP)", data=fp, file_name="district_data_output.zip", mime="application/zip")