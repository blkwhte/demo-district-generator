import streamlit as st
import os
import random
import uuid
import datetime
import re
import pandas as pd
import shutil
from faker import Faker

# ==========================================
# 0. SETUP & CONSTANTS
# ==========================================
fake = Faker('en_US')

DEFAULTS = {
    "ID_MODE": "alphanumeric",
    "OUTPUT_FORMAT": "csv",
    "OUTPUT_SCHEMA": "standard",
    "EMAIL_DOMAIN": "",
    "USERNAME_FMT": "first.last",
    "NUM_DISTRICTS": 1,
    "SCHOOLS_PER_DISTRICT": 5,
    "TEACHERS_PER_SCHOOL": "15-30",
    "STUDENTS_PER_SECTION": "18-32",
    "SECTIONS_PER_TEACHER_TERM": 5,
    "SCHOOL_START_YEAR": "2025",
    "NUM_TERMS": 2,
    "INCLUDE_SUMMER": True,
    "PROB_FRL": 0.45, "PROB_IEP": 0.12, "PROB_ELL": 0.10,
    "PROB_504": 0.05, "PROB_GIFTED": 0.08, "PROB_DISABILITY": 0.11,
    "DO_EXTENSIONS": False, "DO_CONTACTS": True,
    "DO_RESOURCES": False, "DO_ATTENDANCE": False,
    "ATT_START_DATE": "2025-09-01", "ATT_DAYS": 5, "ATT_MODE": "Section" 
}

GENERIC_DISTRICT_NAMES = [ "MapleValley", "OakRiver", "SummitHeights", "PineCreek", "LibertyUnion", "Heritage", "PioneerValley", "GrandView", "Clearwater", "HopeSprings", "NorthStar", "GoldenPlains", "SilverLake", "WillowCreek", "Unity", "CedarRidge" ]
STATE_MAPPINGS = { "C4a": ("California", "CA"), "T3x": ("Texas", "TX"), "N3y": ("New York", "NY"), "F1a": ("Florida", "FL"), "W2a": ("Washington", "WA"), "I1l": ("Illinois", "IL"), "C0l": ("Colorado", "CO"), "A7z": ("Arizona", "AZ"), "G4a": ("Georgia", "GA"), "M4a": ("Massachusetts", "MA") }
STATE_KEYS = list(STATE_MAPPINGS.keys())
REAL_LOCATIONS = {
    "CA": [("San Francisco", "941"), ("Los Angeles", "900")], "TX": [("Austin", "787"), ("Dallas", "752")],
    "NY": [("New York", "100"), ("Brooklyn", "112")], "FL": [("Miami", "331"), ("Orlando", "328")],
    "WA": [("Seattle", "981"), ("Spokane", "992")], "IL": [("Chicago", "606"), ("Peoria", "616")],
    "CO": [("Denver", "802"), ("Boulder", "803")], "AZ": [("Phoenix", "850"), ("Tucson", "857")],
    "GA": [("Atlanta", "303"), ("Savannah", "314")], "MA": [("Boston", "021"), ("Worcester", "016")]
}
CLEVER_RACE_VALUES = ["White", "Black or African American", "Asian", "American Indian or Alaska Native", "Native Hawaiian or Other Pacific Islander", "Two or more races", "Unknown"]
RACE_WEIGHTS = [0.50, 0.15, 0.06, 0.02, 0.01, 0.06, 0.20]
LANGUAGE_MAP = { "eng": 0.70, "spa": 0.20, "vie": 0.03, "zho": 0.02, "ara": 0.02, "tgl": 0.01, "rus": 0.01, "som": 0.01 }
LANG_KEYS, LANG_WEIGHTS = list(LANGUAGE_MAP.keys()), list(LANGUAGE_MAP.values())
DISABILITY_MAP = { "AUT": "Autism", "DB": "Deaf-blindness", "DD": "Developmental delay", "EMN": "Emotional disturbance", "HI": "Hearing impairment", "ID": "Intellectual Disability", "MD": "Multiple disabilities", "OI": "Orthopedic impairment", "OHI": "Other health impairment", "SLD": "Specific learning disability", "SLI": "Speech or language impairment", "TBI": "Traumatic brain injury", "VI": "Visual impairment" }
DISABILITY_CODES = list(DISABILITY_MAP.keys())

# ==========================================
# 1. HELPER FUNCTIONS
# ==========================================
def get_hex_id(length=6): return uuid.uuid4().hex[:length]
def get_sequential_id(base, counter): return str(base + counter)
def clean_phone(): return re.sub("[^0-9]", "", fake.phone_number())[:10]

def parse_count(val_input):
    val_str = str(val_input).strip()
    if "-" in val_str:
        try:
            low, high = map(int, val_str.split("-"))
            return random.randint(low, high)
        except: return 10
    else: return int(val_str)

def generate_dob(grade):
    current_year = datetime.date.today().year
    grade_map = {'PK':4,'KG':5,'1':6,'2':7,'3':8,'4':9,'5':10,'6':11,'7':12,'8':13,'9':14,'10':15,'11':16,'12':17}
    target_age = grade_map.get(grade, 10)
    birth_year = current_year - target_age
    return fake.date_between(start_date=datetime.date(birth_year,1,1), end_date=datetime.date(birth_year,12,31)).strftime('%Y-%m-%d')

def generate_email_username(first, last, domain, fmt):
    f, l = first.lower().replace(" ", ""), last.lower().replace(" ", "")
    if fmt == "first.last": u = f"{f}.{l}"
    elif fmt == "f.last": u = f"{f[0]}.{l}"
    elif fmt == "f_last": u = f"{f[0]}_{l}"
    elif fmt == "flast": u = f"{f}{l}"
    else: u = f"{f}.{l}"
    u = f"{u}{random.randint(10,99)}"
    return u, f"{u}@{domain}"

def generate_term_schedule(anchor_year_str, num_terms):
    y_start = int(anchor_year_str)
    y_end = y_start + 1
    terms = []
    if num_terms == 2:
        terms.append({"Term_name": f"Sem 1 {y_start}", "Term_start": f"{y_start}-08-15", "Term_end": f"{y_start}-12-20"})
        terms.append({"Term_name": f"Sem 2 {y_end}",   "Term_start": f"{y_end}-01-05",   "Term_end": f"{y_end}-05-25"})
    elif num_terms == 3:
        terms.append({"Term_name": f"Tri 1 {y_start}", "Term_start": f"{y_start}-08-15", "Term_end": f"{y_start}-11-10"})
        terms.append({"Term_name": f"Tri 2 {y_start}-{y_end}", "Term_start": f"{y_start}-11-15", "Term_end": f"{y_end}-02-25"})
        terms.append({"Term_name": f"Tri 3 {y_end}",   "Term_start": f"{y_end}-03-01",   "Term_end": f"{y_end}-05-25"})
    elif num_terms == 4:
        terms.append({"Term_name": f"Q1 {y_start}", "Term_start": f"{y_start}-08-15", "Term_end": f"{y_start}-10-15"})
        terms.append({"Term_name": f"Q2 {y_start}", "Term_start": f"{y_start}-10-20", "Term_end": f"{y_start}-12-20"})
        terms.append({"Term_name": f"Q3 {y_end}",   "Term_start": f"{y_end}-01-05",   "Term_end": f"{y_end}-03-15"})
        terms.append({"Term_name": f"Q4 {y_end}",   "Term_start": f"{y_end}-03-20",   "Term_end": f"{y_end}-05-25"})
    return terms

def generate_summer_term(anchor_year_str):
    y_end = int(anchor_year_str) + 1
    return {"Term_name": f"Summer {y_end}", "Term_start": f"{y_end}-06-01", "Term_end": f"{y_end}-07-30"}

def generate_household_contacts(student_last_name, email_domain):
    contacts = []
    rand = random.random()
    def make_contact(rel, type_str, last_n=None):
        if not last_n: last_n = student_last_name
        f_name = fake.first_name_male() if rel in ["Father", "Step-father", "Grandfather"] else fake.first_name_female()
        return { "Contact_relationship": rel, "Contact_type": type_str, "Contact_name": f"{f_name} {last_n}", "Contact_phone": clean_phone(), "Contact_phone_type": random.choice(["Cell", "Home", "Work"]), "Contact_email": f"{f_name}.{last_n}@{email_domain}".lower(), "Contact_sis_id": f"cont-{uuid.uuid4().hex[:8]}" }
    if rand < 0.50: contacts += [make_contact("Mother", "Parent/Guardian"), make_contact("Father", "Parent/Guardian")]
    elif rand < 0.75: contacts.append(make_contact("Mother", "Parent/Guardian"))
    elif rand < 0.85: contacts.append(make_contact("Father", "Parent/Guardian"))
    elif rand < 0.95: contacts += [make_contact("Mother", "Parent/Guardian"), make_contact("Step-father", "Parent/Guardian", fake.last_name())]
    else: contacts.append(make_contact("Grandmother", "Guardian"))
    return contacts

# --- FILE STREAMING HELPERS ---
def init_files(out_dir, schema):
    """Creates empty CSVs with headers."""
    # Define Headers
    HEADERS = {
        "schools": ["School_id", "School_name", "School_number", "Low_grade", "High_grade", "Principal", "Principal_email", "School_address", "School_city", "School_state", "School_zip", "School_phone"],
        "teachers": ["School_id", "Teacher_id", "Teacher_number", "State_teacher_id", "Teacher_email", "Username", "First_name", "Last_name", "Title"],
        "staff": ["School_id", "Staff_id", "Staff_email", "First_name", "Last_name", "Department", "Title"],
        "students": ["School_id", "Student_id", "Student_number", "State_id", "Last_name", "First_name", "Grade", "Gender", "DOB", "Email_address", "Username", "Race", "Home_language", "IEP_status", "FRL_status", "ELL_status", "Section_504_status", "Gifted_status", "Disability_status", "Disability_type", "Disability_code", "ext.locker_number", "ext.bus_route", "Contact_relationship", "Contact_type", "Contact_name", "Contact_phone", "Contact_phone_type", "Contact_email", "Contact_sis_id"],
        "sections": ["School_id", "Section_id", "Teacher_id", "Teacher_2_id", "Name", "Grade", "Subject", "Term_name", "Term_start", "Term_end"],
        "enrollments": ["School_id", "Section_id", "Student_id"],
        "users": ["School_name", "User_type", "User_id", "First_name", "Last_name", "Email", "Username", "Grade", "DOB"],
        "anyschool_sections": ["School_name", "Section_id", "User_id", "Teacher_id", "School_number", "Subject", "Period", "Section_name"]
    }

    paths = {}
    if schema in ["standard", "both"]:
        std_dir = os.path.join(out_dir, "standard")
        os.makedirs(std_dir, exist_ok=True)
        for k in ["schools", "teachers", "staff", "students", "sections", "enrollments"]:
            p = os.path.join(std_dir, f"{k}.csv")
            pd.DataFrame(columns=HEADERS[k]).to_csv(p, index=False)
            paths[f"std_{k}"] = p

    if schema in ["anyschool", "both"]:
        as_dir = os.path.join(out_dir, "anyschool")
        os.makedirs(as_dir, exist_ok=True)
        # Note: AnySchool uses 'sections.csv' but we map it to 'anyschool_sections' key for clarity
        p_users = os.path.join(as_dir, "users.csv")
        p_sec = os.path.join(as_dir, "sections.csv")
        pd.DataFrame(columns=HEADERS["users"]).to_csv(p_users, index=False)
        pd.DataFrame(columns=HEADERS["anyschool_sections"]).to_csv(p_sec, index=False)
        paths["as_users"] = p_users
        paths["as_sections"] = p_sec
        
    return paths

def append_data(data, filepath):
    """Appends a list of dicts to an existing CSV."""
    if not data: return
    df = pd.DataFrame(data)
    # Reorder/Fill columns to match header if necessary, but usually safe if dict keys match
    df.to_csv(filepath, mode='a', header=False, index=False)

def transform_to_anyschool(students, teachers, staff, sections, enrollments, schools):
    school_map = {s['School_id']: {'name': s['School_name'], 'number': s['School_number']} for s in schools}
    
    def fmt_date(d):
        try: return datetime.datetime.strptime(d, "%Y-%m-%d").strftime("%m/%d/%Y")
        except: return d
    
    # --- NEW: CLEVER ANYSCHOOL SCHEMA MAPPINGS ---
    GRADE_MAP = {
        "KG": "Kindergarten", 
        "PK": "PreKindergarten"
    }
    
    SUBJECT_MAP = {
        "Math": "math", 
        "Science": "science", 
        "ELA": "english/language arts",
        "History": "social studies", 
        "Art": "arts and music", 
        "PE": "pe and health",
        "Summer Math": "math", 
        "Summer Reading": "english/language arts",
        "Summer Credit Recovery": "other"
    }

    users_out, sections_out = [], []
    seen_students = set()
    
    # Users (Deduplicating students on the fly)
    for s in students:
        if s['Student_id'] in seen_students: continue
        seen_students.add(s['Student_id'])
        
        # Apply the grade mapping (fallback to original grade number if not KG/PK)
        mapped_grade = GRADE_MAP.get(str(s['Grade']), str(s['Grade']))
        
        users_out.append({"School_name": school_map[s['School_id']]['name'], "User_type": "student", "User_id": s['Student_id'], "First_name": s['First_name'], "Last_name": s['Last_name'], "Email": s['Email_address'], "Username": s.get('Username', ''), "Grade": mapped_grade, "DOB": fmt_date(s['DOB'])})
    
    for t in teachers:
        users_out.append({"School_name": school_map[t['School_id']]['name'], "User_type": "teacher", "User_id": t['Teacher_id'], "First_name": t['First_name'], "Last_name": t['Last_name'], "Email": t['Teacher_email'], "Username": t.get('Username', ''), "Grade": "", "DOB": ""})
    
    for st in staff:
        users_out.append({"School_name": school_map[st['School_id']]['name'], "User_type": "staff", "User_id": st['Staff_id'], "First_name": st['First_name'], "Last_name": st['Last_name'], "Email": st['Staff_email'], "Username": st.get('Staff_email', '').split('@')[0], "Grade": "", "DOB": ""})
    
    # Sections (Flattened)
    sec_lookup = {x['Section_id']: x for x in sections}
    for e in enrollments:
        sd = sec_lookup.get(e['Section_id'])
        if not sd: continue
        
        # Apply the subject mapping (fallback to 'other' if somehow missing)
        mapped_subject = SUBJECT_MAP.get(sd['Subject'], "other")
        
        sections_out.append({"School_name": school_map[e['School_id']]['name'], "Section_id": e['Section_id'], "User_id": e['Student_id'], "Teacher_id": sd['Teacher_id'], "School_number": school_map[e['School_id']]['number'], "Subject": mapped_subject, "Period": "1", "Section_name": sd['Name']})
        
    return users_out, sections_out

# ==========================================
# 2. STREAMLIT UI
# ==========================================
st.set_page_config(page_title="Clever Demo Generator", page_icon="🏫")

st.title("🏫 Clever Demo District Generator")
st.markdown("Generate realistic, privacy-safe school datasets with varied enrollment and term logic.")

# --- SIDEBAR CONFIG ---
with st.sidebar:
    st.header("Configuration")
    st.subheader("Structure")
    num_districts = st.number_input("Number of Districts", min_value=1, value=DEFAULTS["NUM_DISTRICTS"])
    schools_per_district = st.number_input("Schools per District", min_value=1, value=DEFAULTS["SCHOOLS_PER_DISTRICT"])
    
    st.subheader("Format")
    id_mode = st.selectbox("ID Mode", ["alphanumeric", "sequential"], index=0)
    output_schema = st.selectbox("Schema", ["standard", "anyschool", "both"], index=0)
    # Removed JSON support for streaming (complex to stream JSON properly), enforced CSV for large scale
    st.caption("Note: Large scale generation forces CSV format for performance.") 

# --- MAIN FORM ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Ranges & Ratios")
    teachers_input = st.text_input("Teachers per School (Range)", value=DEFAULTS["TEACHERS_PER_SCHOOL"], help="Format: '25' or '15-40'")
    students_input = st.text_input("Students per Section (Range)", value=DEFAULTS["STUDENTS_PER_SECTION"], help="Format: '20' or '15-30'")
    sections_per_teacher = st.number_input("Sections per Teacher (Term)", min_value=1, value=DEFAULTS["SECTIONS_PER_TEACHER_TERM"])

with col2:
    st.subheader("Terms")
    start_year = st.text_input("Start Year (YYYY)", value=DEFAULTS["SCHOOL_START_YEAR"])
    num_terms = st.selectbox("Terms per Year", [2, 3, 4], index=0)
    include_summer = st.checkbox("Include Summer Session?", value=DEFAULTS["INCLUDE_SUMMER"])

with st.expander("Demographics Probabilities"):
    p_frl = st.slider("Free/Reduced Lunch", 0.0, 1.0, DEFAULTS["PROB_FRL"])
    p_iep = st.slider("IEP", 0.0, 1.0, DEFAULTS["PROB_IEP"])
    p_ell = st.slider("ELL", 0.0, 1.0, DEFAULTS["PROB_ELL"])
    p_504 = st.slider("504 Plan", 0.0, 1.0, DEFAULTS["PROB_504"])
    p_gifted = st.slider("Gifted", 0.0, 1.0, DEFAULTS["PROB_GIFTED"])
    p_disability = st.slider("Disability", 0.0, 1.0, DEFAULTS["PROB_DISABILITY"])

with st.expander("Advanced Settings"):
    email_domain = st.text_input("Custom Email Domain", value=DEFAULTS["EMAIL_DOMAIN"], placeholder="Leave empty for auto-gen")
    username_fmt = st.selectbox("Username Format", ["first.last", "f.last", "f_last", "flast"], index=0)
    
    c1, c2, c3, c4 = st.columns(4)
    do_contacts = c1.checkbox("Contacts", value=DEFAULTS["DO_CONTACTS"])
    do_extensions = c2.checkbox("Extensions", value=DEFAULTS["DO_EXTENSIONS"])
    do_resources = c3.checkbox("Resources", value=DEFAULTS["DO_RESOURCES"])
    do_attendance = c4.checkbox("Attendance", value=DEFAULTS["DO_ATTENDANCE"])
    
    if do_attendance:
        att_days = st.number_input("Attendance Days", value=DEFAULTS["ATT_DAYS"])

# ==========================================
# 3. GENERATION LOGIC (STREAMING)
# ==========================================
if st.button("Generate Data", type="primary"):
    
    base_output_dir = 'district_data_output'
    if os.path.exists(base_output_dir):
        shutil.rmtree(base_output_dir)
    os.makedirs(base_output_dir, exist_ok=True)

    random.shuffle(GENERIC_DISTRICT_NAMES)
    CORE_TERMS = generate_term_schedule(start_year, num_terms)
    
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i in range(num_districts):
        dist_name = GENERIC_DISTRICT_NAMES[i % len(GENERIC_DISTRICT_NAMES)]
        status_text.text(f"Generating {dist_name} ({i+1}/{num_districts})...")
        
        # 1. SETUP DISTRICT FOLDER & FILES
        dist_dir = os.path.join(base_output_dir, f"{dist_name}_Data")
        os.makedirs(dist_dir, exist_ok=True)
        file_paths = init_files(dist_dir, output_schema) # Initialize CSVs with headers

        # District Config
        current_domain = email_domain if email_domain else f"{dist_name.lower()}.k12.edu"
        state_key = STATE_KEYS[i % len(STATE_KEYS)]
        state_name, state_abbr = STATE_MAPPINGS[state_key]
        base_id_seq = (i + 1) * 100000 
        
        # --- SCHOOL LOOP (CHUNKED) ---
        for s_idx in range(schools_per_district):
            # Clear chunk containers at start of loop
            chunk_schools, chunk_teachers, chunk_staff = [], [], []
            chunk_students, chunk_sections, chunk_enrollments = [], [], []

            if id_mode == 'alphanumeric': school_id = get_hex_id(6)
            else: school_id = get_sequential_id(base_id_seq, s_idx * 10000)
            
            school_type = random.choice(['Elementary', 'Middle', 'High', 'Academy'])
            school_code = f"{s_idx + 1:02d}"
            if 'Elementary' in school_type: low, high = 'KG', '5'
            elif 'Middle' in school_type: low, high = '6', '8'
            elif 'High' in school_type: low, high = '9', '12'
            else: low, high = 'KG', '12'
            
            valid_locs = REAL_LOCATIONS.get(state_abbr, [("City", "000")])
            city, zip_pre = random.choice(valid_locs)
            
            chunk_schools.append({
                "School_id": school_id, "School_name": f"{fake.last_name()} {school_type}",
                "School_number": school_code, "Low_grade": low, "High_grade": high,
                "Principal": fake.name(), "Principal_email": f"principal.{school_id}@{current_domain}",
                "School_address": fake.street_address(), "School_city": city, "School_state": state_abbr, "School_zip": f"{zip_pre}{random.randint(10, 99)}", "School_phone": fake.phone_number()
            })

            # --- TEACHERS ---
            num_teachers = parse_count(teachers_input)
            school_teacher_ids = []
            for t_idx in range(num_teachers):
                t_id = get_hex_id(7) if id_mode == 'alphanumeric' else get_sequential_id(base_id_seq, (s_idx * 1000) + t_idx)
                f, l = fake.first_name(), fake.last_name()
                uname, email = generate_email_username(f, l, current_domain, username_fmt)
                chunk_teachers.append({
                    "School_id": school_id, "Teacher_id": t_id, "Teacher_number": t_id[:8], "State_teacher_id": f"{state_abbr}-{t_id[:8]}",
                    "Teacher_email": email, "Username": uname, "First_name": f, "Last_name": l, "Title": "Teacher"
                })
                school_teacher_ids.append(t_id)

            # --- STAFF ---
            for st_idx in range(2):
                st_id = get_hex_id(7) if id_mode == 'alphanumeric' else get_sequential_id(base_id_seq, 90000 + (s_idx*10) + st_idx)
                f, l = fake.first_name(), fake.last_name()
                uname, email = generate_email_username(f, l, current_domain, username_fmt)
                chunk_staff.append({
                    "School_id": school_id, "Staff_id": st_id, "Staff_email": email, "First_name": f, "Last_name": l, "Department": "Admin", "Title": "Staff"
                })

            # --- SECTIONS (Ratio) ---
            grade_list = [str(g) if g > 0 else 'KG' for g in range(int(low) if low.isdigit() else 0, (int(high) if high.isdigit() else 12) + 1)]
            school_section_ids = []

            for t_id in school_teacher_ids:
                for term in CORE_TERMS:
                    for _ in range(sections_per_teacher):
                        sec_id = get_hex_id(8) if id_mode == 'alphanumeric' else f"SEC-{uuid.uuid4().hex[:8]}"
                        s_grade = random.choice(grade_list)
                        s_subj = random.choice(['Math', 'Science', 'ELA', 'History', 'Art', 'PE'])
                        chunk_sections.append({
                            "School_id": school_id, "Section_id": sec_id, "Teacher_id": t_id, "Teacher_2_id": "",
                            "Name": f"{s_grade} - {s_subj}", "Grade": s_grade, "Subject": s_subj,
                            "Term_name": term["Term_name"], "Term_start": term["Term_start"], "Term_end": term["Term_end"]
                        })
                        school_section_ids.append({"id": sec_id, "grade": s_grade})

            # --- STUDENTS ---
            avg_sec_size = parse_count(students_input)
            estimated_students = int((len(school_section_ids) * avg_sec_size) / sections_per_teacher)
            school_student_objs = []
            
            for stu_idx in range(estimated_students):
                stu_id = get_hex_id(6) if id_mode == 'alphanumeric' else get_sequential_id(base_id_seq, 200000 + (s_idx * 5000) + stu_idx)
                f, l = fake.first_name(), fake.last_name()
                uname, email = generate_email_username(f, l, current_domain, username_fmt)
                s_grade = random.choice(grade_list)
                
                has_disability = "Y" if random.random() < p_disability else "N"
                dis_code, dis_type = ("", "")
                if has_disability == "Y":
                    c = random.choice(DISABILITY_CODES)
                    dis_code, dis_type = c, DISABILITY_MAP[c]
                
                stu_obj = {
                    "School_id": school_id, "Student_id": stu_id, "Student_number": stu_id[:8], "State_id": f"{state_abbr}-{stu_id[:8]}",
                    "Last_name": l, "First_name": f, "Grade": s_grade, "Gender": random.choice(['M', 'F']),
                    "DOB": generate_dob(s_grade), "Email_address": email, "Username": uname,
                    "Race": random.choices(CLEVER_RACE_VALUES, weights=RACE_WEIGHTS)[0],
                    "Home_language": random.choices(LANG_KEYS, weights=LANG_WEIGHTS)[0],
                    "IEP_status": "Y" if random.random() < p_iep else "N", "FRL_status": "Y" if random.random() < p_frl else "N",
                    "ELL_status": "Y" if random.random() < p_ell else "N", "Section_504_status": "Y" if random.random() < p_504 else "N",
                    "Gifted_status": "Y" if random.random() < p_gifted else "N", "Disability_status": has_disability, "Disability_type": dis_type, "Disability_code": dis_code
                }
                if do_extensions: stu_obj['ext.locker_number'], stu_obj['ext.bus_route'] = random.randint(100, 9999), random.choice(['Route A', 'Route B'])
                
                school_student_objs.append(stu_obj)
                
                if do_contacts:
                    hh = generate_household_contacts(l, current_domain)
                    for c in hh:
                        r = stu_obj.copy()
                        r.update(c)
                        chunk_students.append(r)
                else:
                    chunk_students.append(stu_obj)

            # --- ENROLLMENT ---
            students_by_grade = {g: [s for s in school_student_objs if s['Grade'] == g] for g in grade_list}
            for sec in school_section_ids:
                avail = students_by_grade.get(sec['grade'], [])
                if not avail: continue
                count = parse_count(students_input)
                selected = random.sample(avail, k=min(count, len(avail)))
                for s in selected:
                    chunk_enrollments.append({"School_id": school_id, "Section_id": sec['id'], "Student_id": s['Student_id']})

            # --- SUMMER ---
            if include_summer:
                summer_term = generate_summer_term(start_year)
                k_teach = int(len(school_teacher_ids) * 0.35)
                summer_teachers = random.sample(school_teacher_ids, k=max(1, k_teach))
                summer_sections = []
                for st_id in summer_teachers:
                    for _ in range(random.randint(1,2)):
                        sec_id = f"SUM-{uuid.uuid4().hex[:6]}"
                        s_grade = random.choice(grade_list)
                        s_subj = "Summer " + random.choice(['Math', 'Reading', 'Credit Recovery'])
                        chunk_sections.append({
                            "School_id": school_id, "Section_id": sec_id, "Teacher_id": st_id, "Teacher_2_id": "",
                            "Name": f"{s_grade} - {s_subj}", "Grade": s_grade, "Subject": s_subj,
                            "Term_name": summer_term["Term_name"], "Term_start": summer_term["Term_start"], "Term_end": summer_term["Term_end"]
                        })
                        summer_sections.append({"id": sec_id, "grade": s_grade})
                
                k_stu = int(len(school_student_objs) * 0.30)
                summer_students = random.sample(school_student_objs, k=max(1, k_stu))
                summer_students_by_grade = {g: [s for s in summer_students if s['Grade'] == g] for g in grade_list}
                for sec in summer_sections:
                    avail = summer_students_by_grade.get(sec['grade'], [])
                    if not avail: continue
                    count = random.randint(10, 20)
                    selected = random.sample(avail, k=min(count, len(avail)))
                    for s in selected:
                        chunk_enrollments.append({"School_id": school_id, "Section_id": sec['id'], "Student_id": s['Student_id']})

            # --- ADMIN (One per district, so just do it on first school) ---
            if s_idx == 0:
                 admin_id = get_hex_id(7) if id_mode == 'alphanumeric' else str(base_id_seq + 99999)
                 chunk_staff.insert(0, { "School_id": school_id, "Staff_id": admin_id, "Staff_email": f"admin@{current_domain}", "First_name": "System", "Last_name": "Admin", "Department": "Central", "Title": "Admin" })

            # --- STREAM TO DISK NOW (FLUSH MEMORY) ---
            if "std_schools" in file_paths:
                append_data(chunk_schools, file_paths["std_schools"])
                append_data(chunk_teachers, file_paths["std_teachers"])
                append_data(chunk_staff, file_paths["std_staff"])
                append_data(chunk_students, file_paths["std_students"])
                append_data(chunk_sections, file_paths["std_sections"])
                append_data(chunk_enrollments, file_paths["std_enrollments"])

            if "as_users" in file_paths:
                # Transform this chunk
                u_chunk, s_chunk = transform_to_anyschool(chunk_students, chunk_teachers, chunk_staff, chunk_sections, chunk_enrollments, chunk_schools)
                append_data(u_chunk, file_paths["as_users"])
                append_data(s_chunk, file_paths["as_sections"])

            # Explicitly clear large lists to force memory release (Python GC is usually good, but this helps)
            del chunk_students, chunk_enrollments, chunk_sections
        
        progress_bar.progress((i + 1) / num_districts)

    status_text.success("Generation Complete! Creating Archive...")
    
    shutil.make_archive(base_output_dir, 'zip', base_output_dir)
    
    with open(f"{base_output_dir}.zip", "rb") as fp:
        btn = st.download_button(
            label="Download Data (ZIP)",
            data=fp,
            file_name="district_data_output.zip",
            mime="application/zip"
        )