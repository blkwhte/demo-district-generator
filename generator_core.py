import os
import random
import uuid
import datetime
import re
import pandas as pd
from faker import Faker

fake = Faker('en_US')

# ==========================================
# 1. CONSTANTS & DEFAULTS
# ==========================================
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
    "PROB_FRL": 0.45, 
    "PROB_IEP": 0.12, 
    "PROB_ELL": 0.10,
    "PROB_504": 0.05, 
    "PROB_GIFTED": 0.08, 
    "PROB_DISABILITY": 0.11,
    "DO_EXTENSIONS": False, 
    "DO_CONTACTS": True, 
    "DO_RESOURCES": False, 
    "DO_ATTENDANCE": False,
    "ATT_START_DATE": "2025-09-01", 
    "ATT_DAYS": 5, 
    "ATT_MODE": "Section",
    "DO_3_DAY_ROTATION": False
}

GENERIC_DISTRICT_NAMES = [ "MapleValley", "OakRiver", "SummitHeights", "PineCreek", "LibertyUnion", "Heritage", "PioneerValley", "GrandView", "Clearwater", "HopeSprings", "NorthStar", "GoldenPlains", "SilverLake", "WillowCreek", "Unity", "CedarRidge" ]
STATE_MAPPINGS = { "C4a": ("California", "CA"), "T3x": ("Texas", "TX"), "N3y": ("New York", "NY"), "F1a": ("Florida", "FL"), "W2a": ("Washington", "WA"), "I1l": ("Illinois", "IL"), "C0l": ("Colorado", "CO"), "A7z": ("Arizona", "AZ"), "G4a": ("Georgia", "GA"), "M4a": ("Massachusetts", "MA") }
STATE_KEYS = list(STATE_MAPPINGS.keys())
REAL_LOCATIONS = {
    "CA": [("San Francisco", "941"), ("Los Angeles", "900")], "TX": [("Austin", "787"), ("Dallas", "752")],
    "NY": [("New York", "100"), ("Brooklyn", "112")], "FL": [("Miami", "331"), ("Orlando", "328")]
}
CLEVER_RACE_VALUES = ["White", "Black or African American", "Asian", "American Indian or Alaska Native", "Native Hawaiian or Other Pacific Islander", "Two or more races", "Unknown"]
RACE_WEIGHTS = [0.50, 0.15, 0.06, 0.02, 0.01, 0.06, 0.20]
LANG_KEYS = ["eng", "spa", "vie", "zho", "ara"]
LANG_WEIGHTS = [0.70, 0.20, 0.05, 0.03, 0.02]
DISABILITY_MAP = { "AUT": "Autism", "SLD": "Specific learning disability", "SLI": "Speech or language impairment" }
DISABILITY_CODES = list(DISABILITY_MAP.keys())

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================
def get_hex_id(length=6): return uuid.uuid4().hex[:length]
def get_sequential_id(base, counter): return str(base + counter)
def clean_phone(): 
    digits = re.sub("[^0-9]", "", fake.phone_number())
    if len(digits) < 10: digits = digits.ljust(10, '0')
    digits = digits[:10]
    return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"

def parse_count(val_input):
    val_str = str(val_input).strip()
    if "-" in val_str:
        try:
            low, high = map(int, val_str.split("-"))
            return max(1, random.randint(low, high))
        except: return 10
    else: 
        try: return max(1, int(val_str))
        except: return 10

def generate_dob(grade):
    current_year = datetime.date.today().year
    grade_map = {'PK':4,'KG':5,'1':6,'2':7,'3':8,'4':9,'5':10,'6':11,'7':12,'8':13,'9':14,'10':15,'11':16,'12':17}
    return fake.date_between(start_date=datetime.date(current_year - grade_map.get(grade, 10),1,1), end_date=datetime.date(current_year - grade_map.get(grade, 10),12,31)).strftime('%Y-%m-%d')

def generate_email_username(first, last, domain, fmt):
    f, l = first.lower().replace(" ", ""), last.lower().replace(" ", "")
    # Sanitize for actual email address logic (even if name has apostrophes)
    f, l = re.sub(r'[^a-z]', '', f), re.sub(r'[^a-z]', '', l)
    u = f"{f}.{l}{random.randint(10,99)}"
    return u, f"{u}@{domain}"

def generate_term_schedule(anchor_year_str, num_terms):
    y_start = int(anchor_year_str)
    y_end = y_start + 1
    terms = []
    if num_terms == 2:
        terms.append({"Term_name": f"Sem 1 {y_start}", "Term_start": f"{y_start}-08-15", "Term_end": f"{y_start}-12-20"})
        terms.append({"Term_name": f"Sem 2 {y_end}",   "Term_start": f"{y_end}-01-05",   "Term_end": f"{y_end}-05-25"})
    return terms

def generate_summer_term(anchor_year_str):
    y_end = int(anchor_year_str) + 1
    return {"Term_name": f"Summer {y_end}", "Term_start": f"{y_end}-06-01", "Term_end": f"{y_end}-07-30"}

def generate_household_contacts(student_last_name):
    rel_options = [("Mother", "female", "Parent/Guardian"), ("Father", "male", "Parent/Guardian"), ("Grandmother", "female", "Emergency"), ("Grandfather", "male", "Emergency"), ("Aunt", "female", "Emergency"), ("Uncle", "male", "Emergency"), ("Guardian", "neutral", "Parent/Guardian")]
    weights = [40, 40, 5, 5, 3, 3, 4] 
    choice = random.choices(rel_options, weights=weights, k=1)[0]
    relationship, gender, contact_type = choice
    
    if gender == "female": f_name = fake.first_name_female()
    elif gender == "male": f_name = fake.first_name_male()
    else: f_name = fake.first_name()
        
    return [{ 
        "Contact_relationship": relationship, 
        "Contact_type": contact_type, 
        "Contact_name": f"{f_name} {student_last_name}", 
        "Contact_phone": clean_phone(), 
        "Contact_phone_type": "Cell", 
        "Contact_email": f"{re.sub(r'[^a-z]', '', f_name.lower())}.{re.sub(r'[^a-z]', '', student_last_name.lower())}@example.com", 
        "Contact_sis_id": f"cont-{uuid.uuid4().hex[:8]}" 
    }]

# --- FILE STREAMING HELPERS ---
def init_files(out_dir, schema):
    HEADERS = {
        "schools": ["School_id", "School_name", "School_number", "Low_grade", "High_grade", "Principal", "Principal_email", "School_address", "School_city", "School_state", "School_zip", "School_phone"],
        "teachers": ["School_id", "Teacher_id", "Teacher_number", "State_teacher_id", "Teacher_email", "Username", "First_name", "Last_name", "Title"],
        "staff": ["School_id", "Staff_id", "Staff_email", "First_name", "Last_name", "Department", "Title"],
        "students": ["School_id", "Student_id", "Student_number", "State_id", "Last_name", "First_name", "Grade", "Gender", "DOB", "Student_email", "Username", "Race", "Home_language", "IEP_status", "FRL_status", "ELL_status", "Section_504_status", "Gifted_status", "Disability_status", "Disability_type", "Disability_code", "ext.locker_number", "ext.bus_route", "Contact_relationship", "Contact_type", "Contact_name", "Contact_phone", "Contact_phone_type", "Contact_email", "Contact_sis_id"],
        "sections": ["School_id", "Section_id", "Teacher_id", "Teacher_2_id", "Name", "Grade", "Subject", "Term_name", "Term_start", "Term_end", "Period"],
        "enrollments": ["School_id", "Section_id", "Student_id"],
        "attendance": ["Attendance_id", "School_id", "Student_id", "Section_id", "Attendance_date", "Attendance_status", "Attendance_type", "Excuse_code"],
        "users": ["School_name", "User_type", "User_id", "First_name", "Last_name", "Email", "Username", "Grade", "DOB"],
        "anyschool_sections": ["School_name", "Section_id", "User_id", "Teacher_id", "School_number", "Subject", "Period", "Section_name"]
    }
    paths = {}
    if schema in ["standard", "both"]:
        std_dir = os.path.join(out_dir, "standard")
        os.makedirs(std_dir, exist_ok=True)
        for k in ["schools", "teachers", "staff", "students", "sections", "enrollments", "attendance"]:
            p = os.path.join(std_dir, f"{k}.csv")
            pd.DataFrame(columns=HEADERS[k]).to_csv(p, index=False)
            paths[f"std_{k}"] = p

    if schema in ["anyschool", "both"]:
        as_dir = os.path.join(out_dir, "anyschool")
        os.makedirs(as_dir, exist_ok=True)
        paths["as_users"] = os.path.join(as_dir, "users.csv")
        paths["as_sections"] = os.path.join(as_dir, "sections.csv")
        pd.DataFrame(columns=HEADERS["users"]).to_csv(paths["as_users"], index=False)
        pd.DataFrame(columns=HEADERS["anyschool_sections"]).to_csv(paths["as_sections"], index=False)
    return paths

def append_data(data, filepath):
    if data: pd.DataFrame(data).to_csv(filepath, mode='a', header=False, index=False)

def transform_to_anyschool(students, teachers, staff, sections, enrollments, schools):
    school_map = {s['School_id']: {'name': s['School_name'], 'number': s['School_number']} for s in schools}
    def fmt_date(d):
        try: return datetime.datetime.strptime(d, "%Y-%m-%d").strftime("%m/%d/%Y")
        except: return d
    
    GRADE_MAP = {"KG": "Kindergarten", "PK": "PreKindergarten"}
    SUBJECT_MAP = { "Math": "math", "Science": "science", "ELA": "english/language arts", "History": "social studies", "Art": "arts and music", "PE": "pe and health", "Summer Math": "math", "Summer Reading": "english/language arts", "Summer Credit Recovery": "other" }

    users_out, sections_out = [], []
    seen_students = set()
    
    for s in students:
        if s['Student_id'] in seen_students: continue
        seen_students.add(s['Student_id'])
        mapped_grade = GRADE_MAP.get(str(s['Grade']), str(s['Grade']))
        users_out.append({"School_name": school_map[s['School_id']]['name'], "User_type": "student", "User_id": s['Student_id'], "First_name": s['First_name'], "Last_name": s['Last_name'], "Email": s['Student_email'], "Username": s.get('Username', ''), "Grade": mapped_grade, "DOB": fmt_date(s['DOB'])})
    
    for t in teachers: users_out.append({"School_name": school_map[t['School_id']]['name'], "User_type": "teacher", "User_id": t['Teacher_id'], "First_name": t['First_name'], "Last_name": t['Last_name'], "Email": t['Teacher_email'], "Username": t.get('Username', ''), "Grade": "", "DOB": ""})
    for st in staff: users_out.append({"School_name": school_map[st['School_id']]['name'], "User_type": "staff", "User_id": st['Staff_id'], "First_name": st['First_name'], "Last_name": st['Last_name'], "Email": st['Staff_email'], "Username": st.get('Staff_email', '').split('@')[0], "Grade": "", "DOB": ""})
    
    sec_lookup = {x['Section_id']: x for x in sections}
    for e in enrollments:
        sd = sec_lookup.get(e['Section_id'])
        if not sd: continue
        mapped_subject = SUBJECT_MAP.get(sd['Subject'], "other")
        sections_out.append({"School_name": school_map[e['School_id']]['name'], "Section_id": e['Section_id'], "User_id": e['Student_id'], "Teacher_id": sd['Teacher_id'], "School_number": school_map[e['School_id']]['number'], "Subject": mapped_subject, "Period": sd.get('Period', "1"), "Section_name": sd['Name']})
        
    return users_out, sections_out

# --- NEW: BATCH EXPORT HELPER ---
def export_district_state(config, base_dir, dist_name, folder_suffix, db):
    """Writes the current state of the district memory database to CSVs"""
    out_dir = os.path.join(base_dir, f"{dist_name}_{folder_suffix}")
    os.makedirs(out_dir, exist_ok=True)
    file_paths = init_files(out_dir, config["OUTPUT_SCHEMA"])

    if "std_schools" in file_paths:
        for data, key in [(db["schools"], "std_schools"), (db["teachers"], "std_teachers"), (db["staff"], "std_staff"), (db["students"], "std_students"), (db["sections"], "std_sections"), (db["enrollments"], "std_enrollments"), (db["attendance"], "std_attendance")]:
            append_data(data, file_paths[key])
            
    if "as_users" in file_paths:
        u_chunk, s_chunk = transform_to_anyschool(db["students"], db["teachers"], db["staff"], db["sections"], db["enrollments"], db["schools"])
        append_data(u_chunk, file_paths["as_users"])
        append_data(s_chunk, file_paths["as_sections"])

# ==========================================
# 3. MAIN GENERATION ENGINE
# ==========================================
def run_generation(config, base_output_dir, status_callback=None, progress_callback=None):
    random.shuffle(GENERIC_DISTRICT_NAMES)
    CORE_TERMS = generate_term_schedule(config["SCHOOL_START_YEAR"], config["NUM_TERMS"])
    do_3_day = config.get("DO_3_DAY_ROTATION", False)
    
    # --- TRACK EDGE CASES FOR REPORT ---
    edge_case_report = {
        "Scenario 9 (Missing @ in Email)": [],
        "Scenario 10 (Special characters in Name)": [],
        "Scenario 12 (Short Name)": [],
        "Scenario 15 (Student Deleted Day 2, Restored Day 3)": [],
        "Scenario 16 (Section Deleted Day 2, Restored Day 3)": [],
        "Scenario 35 (Contact ID changes Day 2)": [],
        "Scenario 38 (Student Transfers School Day 3)": []
    }
    
    for i in range(config["NUM_DISTRICTS"]):
        dist_name = GENERIC_DISTRICT_NAMES[i % len(GENERIC_DISTRICT_NAMES)]
        if status_callback: status_callback(f"Generating {dist_name}...")

        current_domain = config["EMAIL_DOMAIN"] if config["EMAIL_DOMAIN"] else f"{dist_name.lower()}.k12.edu"
        state_key = STATE_KEYS[i % len(STATE_KEYS)]
        state_name, state_abbr = STATE_MAPPINGS[state_key]
        base_id_seq = (i + 1) * 100000 
        
        # --- HOLD ENTIRE DISTRICT IN MEMORY FOR MUTATIONS ---
        dist_db = { "schools": [], "teachers": [], "staff": [], "students": [], "sections": [], "enrollments": [], "attendance": [] }
        
        for s_idx in range(config["SCHOOLS_PER_DISTRICT"]):
            school_id = get_hex_id(6) if config["ID_MODE"] == 'alphanumeric' else get_sequential_id(base_id_seq, s_idx * 10000)
            school_type = random.choice(['Elementary', 'Middle', 'High', 'Academy'])
            school_code = f"{s_idx + 1:02d}"
            low, high = ('KG', '5') if 'Elementary' in school_type else ('6', '8') if 'Middle' in school_type else ('9', '12') if 'High' in school_type else ('KG', '12')
            city, zip_pre = random.choice(REAL_LOCATIONS.get(state_abbr, [("City", "000")]))
            
            prin_first, prin_last = fake.first_name(), fake.last_name()
            prin_email = f"principal.{school_id}@{current_domain}"
            
            dist_db["schools"].append({"School_id": school_id, "School_name": f"{fake.last_name()} {school_type}", "School_number": school_code, "Low_grade": low, "High_grade": high, "Principal": f"{prin_first} {prin_last}", "Principal_email": prin_email, "School_address": fake.street_address(), "School_city": city, "School_state": state_abbr, "School_zip": f"{zip_pre}{random.randint(10, 99)}", "School_phone": fake.phone_number()})
            dist_db["staff"].append({"School_id": school_id, "Staff_id": get_hex_id(7) if config["ID_MODE"] == 'alphanumeric' else get_sequential_id(base_id_seq, 90000 + s_idx), "Staff_email": prin_email, "First_name": prin_first, "Last_name": prin_last, "Department": "Administration", "Title": "Principal"})

            num_teachers = parse_count(config["TEACHERS_PER_SCHOOL"])
            school_teacher_ids = []
            
            for t_idx in range(num_teachers):
                t_id = get_hex_id(7) if config["ID_MODE"] == 'alphanumeric' else get_sequential_id(base_id_seq, (s_idx * 1000) + t_idx)
                f, l = fake.first_name(), fake.last_name()
                uname, email = generate_email_username(f, l, current_domain, config["USERNAME_FMT"])
                
                dist_db["teachers"].append({"School_id": school_id, "Teacher_id": t_id, "Teacher_number": t_id[:8], "State_teacher_id": f"{state_abbr}-{t_id[:8]}", "Teacher_email": email, "Username": uname, "First_name": f, "Last_name": l, "Title": "Teacher"})
                school_teacher_ids.append(t_id)

            if dist_db["teachers"]:
                multi_role = dist_db["teachers"][-len(school_teacher_ids)] # Grab first teacher of this school
                dist_db["staff"].append({"School_id": school_id, "Staff_id": get_hex_id(7) if config["ID_MODE"] == 'alphanumeric' else get_sequential_id(base_id_seq, 80000 + s_idx), "Staff_email": multi_role["Teacher_email"], "First_name": multi_role["First_name"], "Last_name": multi_role["Last_name"], "Department": "Academics", "Title": "Department Chair"})

            grade_list = [str(g) if g > 0 else 'KG' for g in range(int(low) if low.isdigit() else 0, (int(high) if high.isdigit() else 12) + 1)]
            school_section_ids = []

            for t_id in school_teacher_ids:
                for term in CORE_TERMS:
                    for period_idx in range(config["SECTIONS_PER_TEACHER_TERM"]):
                        sec_id = get_hex_id(8) if config["ID_MODE"] == 'alphanumeric' else f"SEC-{uuid.uuid4().hex[:8]}"
                        s_grade, s_subj = random.choice(grade_list), random.choice(['Math', 'Science', 'ELA', 'History', 'Art', 'PE'])
                        dist_db["sections"].append({"School_id": school_id, "Section_id": sec_id, "Teacher_id": t_id, "Teacher_2_id": "", "Name": f"{s_grade} - {s_subj}", "Grade": s_grade, "Subject": s_subj, "Term_name": term["Term_name"], "Term_start": term["Term_start"], "Term_end": term["Term_end"], "Period": str(period_idx + 1)})
                        school_section_ids.append({"id": sec_id, "grade": s_grade})

            avg_sec_size = parse_count(config["STUDENTS_PER_SECTION"])
            estimated_students = int((len(school_section_ids) * avg_sec_size) / config["SECTIONS_PER_TEACHER_TERM"])
            school_student_objs = []
            
            for stu_idx in range(estimated_students):
                stu_id = get_hex_id(6) if config["ID_MODE"] == 'alphanumeric' else get_sequential_id(base_id_seq, 200000 + (s_idx * 5000) + stu_idx)
                f, l = fake.first_name(), fake.last_name()
                
                # --- STATIC EDGE CASES (Day 1 anomalies) ---
                if do_3_day:
                    r_val = random.random()
                    if r_val < 0.02: 
                        l = "O'Connor" # Scenario 10
                        edge_case_report["Scenario 10 (Special characters in Name)"].append(f"Student_id: {stu_id}")
                    elif r_val < 0.04: 
                        l = "Nuñez"  # Scenario 10
                        edge_case_report["Scenario 10 (Special characters in Name)"].append(f"Student_id: {stu_id}")
                    elif r_val < 0.06: 
                        l = "Li"     # Scenario 12
                        edge_case_report["Scenario 12 (Short Name)"].append(f"Student_id: {stu_id}")
                
                uname, email = generate_email_username(f, l, current_domain, config["USERNAME_FMT"])
                
                if do_3_day and random.random() < 0.01: 
                    email = email.replace("@", "") # Scenario 9
                    edge_case_report["Scenario 9 (Missing @ in Email)"].append(f"Student_id: {stu_id}")
                
                s_grade = random.choice(grade_list)
                has_disability = "Y" if random.random() < config["PROB_DISABILITY"] else "N"
                dis_code, dis_type = (random.choice(DISABILITY_CODES), DISABILITY_MAP[random.choice(DISABILITY_CODES)]) if has_disability == "Y" else ("", "")
                
                stu_obj = {
                    "School_id": school_id, "Student_id": stu_id, "Student_number": stu_id[:8], "State_id": f"{state_abbr}-{stu_id[:8]}", 
                    "Last_name": l, "First_name": f, "Grade": s_grade, "Gender": random.choice(['M', 'F']), 
                    "DOB": generate_dob(s_grade), "Student_email": email, "Username": uname, 
                    "Race": random.choices(CLEVER_RACE_VALUES, weights=RACE_WEIGHTS)[0], 
                    "Home_language": random.choices(LANG_KEYS, weights=LANG_WEIGHTS)[0], 
                    "IEP_status": "Y" if random.random() < config["PROB_IEP"] else "N", "FRL_status": "Y" if random.random() < config["PROB_FRL"] else "N", 
                    "ELL_status": "Y" if random.random() < config["PROB_ELL"] else "N", "Section_504_status": "Y" if random.random() < config["PROB_504"] else "N", 
                    "Gifted_status": "Y" if random.random() < config["PROB_GIFTED"] else "N", "Disability_status": has_disability, "Disability_type": dis_type, "Disability_code": dis_code,
                    "ext.locker_number": "", "ext.bus_route": "", "Contact_relationship": "", "Contact_type": "", "Contact_name": "", "Contact_phone": "", "Contact_phone_type": "", "Contact_email": "", "Contact_sis_id": ""
                }
                
                school_student_objs.append(stu_obj)
                if config["DO_CONTACTS"]:
                    for c in generate_household_contacts(l):
                        r = stu_obj.copy()
                        r.update(c)
                        dist_db["students"].append(r)
                else: dist_db["students"].append(stu_obj)

            students_by_grade = {g: [s for s in school_student_objs if s['Grade'] == g] for g in grade_list}
            for sec in school_section_ids:
                avail = students_by_grade.get(sec['grade'], [])
                if avail:
                    for s in random.sample(avail, k=min(parse_count(config["STUDENTS_PER_SECTION"]), len(avail))):
                        dist_db["enrollments"].append({"School_id": school_id, "Section_id": sec['id'], "Student_id": s['Student_id']})

            if s_idx == 0:
                 dist_db["staff"].insert(0, { "School_id": school_id, "Staff_id": get_hex_id(7) if config["ID_MODE"] == 'alphanumeric' else str(base_id_seq + 99999), "Staff_email": f"admin@{current_domain}", "First_name": "System", "Last_name": "Admin", "Department": "Central", "Title": "Admin" })

        # --- 3-DAY ROTATION ENGINE ---
        if not do_3_day:
            export_district_state(config, base_output_dir, dist_name, "Data", dist_db)
        else:
            if status_callback: status_callback(f"Generating {dist_name} Day 1...")
            export_district_state(config, base_output_dir, dist_name, "Day_1", dist_db)

            # ----- DAY 2 MUTATIONS -----
            if status_callback: status_callback(f"Generating {dist_name} Day 2...")
            
            # Scenario 15: Student is deleted on Day 2
            mia_student = dist_db["students"].pop(random.randint(0, len(dist_db["students"]) - 1))
            mia_student_enrollments = [e for e in dist_db["enrollments"] if e["Student_id"] == mia_student["Student_id"]]
            dist_db["enrollments"] = [e for e in dist_db["enrollments"] if e["Student_id"] != mia_student["Student_id"]]
            edge_case_report["Scenario 15 (Student Deleted Day 2, Restored Day 3)"].append(f"Student_id: {mia_student['Student_id']}")
            
            # Scenario 16: Section removed on Day 2
            mia_section = dist_db["sections"].pop(random.randint(0, len(dist_db["sections"]) - 1))
            mia_section_enrollments = [e for e in dist_db["enrollments"] if e["Section_id"] == mia_section["Section_id"]]
            dist_db["enrollments"] = [e for e in dist_db["enrollments"] if e["Section_id"] != mia_section["Section_id"]]
            edge_case_report["Scenario 16 (Section Deleted Day 2, Restored Day 3)"].append(f"Section_id: {mia_section['Section_id']}")

            # Scenario 35: Student contact ID changes Day over Day
            if dist_db["students"]:
                dist_db["students"][0]["Contact_sis_id"] = f"cont-{uuid.uuid4().hex[:8]}"
                edge_case_report["Scenario 35 (Contact ID changes Day 2)"].append(f"Student_id: {dist_db['students'][0]['Student_id']} (Contact ID changed)")

            export_district_state(config, base_output_dir, dist_name, "Day_2", dist_db)

            # ----- DAY 3 MUTATIONS -----
            if status_callback: status_callback(f"Generating {dist_name} Day 3...")
            
            # Scenario 15/16 (Restored): Student and Section return
            dist_db["students"].append(mia_student)
            dist_db["sections"].append(mia_section)
            dist_db["enrollments"].extend(mia_student_enrollments)
            dist_db["enrollments"].extend(mia_section_enrollments)

            # Scenario 38: Student transfers to a new school
            if len(dist_db["schools"]) > 1:
                transfer_student = dist_db["students"][1]
                old_school = transfer_student["School_id"]
                new_school = next(s["School_id"] for s in dist_db["schools"] if s["School_id"] != old_school)
                
                # Update school ID and strip old enrollments
                for r in dist_db["students"]:
                    if r["Student_id"] == transfer_student["Student_id"]:
                        r["School_id"] = new_school
                dist_db["enrollments"] = [e for e in dist_db["enrollments"] if e["Student_id"] != transfer_student["Student_id"]]
                
                edge_case_report["Scenario 38 (Student Transfers School Day 3)"].append(f"Student_id: {transfer_student['Student_id']} (Moved from {old_school} -> {new_school})")

            export_district_state(config, base_output_dir, dist_name, "Day_3", dist_db)

        # --- WRITE THE EDGE CASE REPORT ---
        if do_3_day:
            report_path = os.path.join(base_output_dir, f"{dist_name}_edge_cases_report.txt")
            with open(report_path, "w") as f:
                f.write(f"CLEVER DEMO DISTRICT - EDGE CASES REPORT: {dist_name}\n")
                f.write("=========================================================\n\n")
                for scenario, ids in edge_case_report.items():
                    f.write(f"{scenario}:\n")
                    if not ids:
                        f.write("  None generated in this run.\n")
                    for item in ids:
                        f.write(f"  - {item}\n")
                    f.write("\n")

        if progress_callback: progress_callback((i + 1) / config["NUM_DISTRICTS"])