import os
import random
import uuid
import datetime
import re
import pandas as pd
from faker import Faker
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.prompt import IntPrompt, Confirm, Prompt, FloatPrompt

fake = Faker('en_US')
console = Console()

# ==========================================
# 1. DEFAULT CONFIGURATION
# ==========================================
DEFAULTS = {
    "ID_MODE": "alphanumeric",
    "OUTPUT_FORMAT": "csv",
    "OUTPUT_SCHEMA": "standard",
    
    "EMAIL_DOMAIN": "",
    "USERNAME_FMT": "first.last",
    
    "NUM_DISTRICTS": 1,
    "SCHOOLS_PER_DISTRICT": 5,
    
    # NEW: Ranges (Strings allowing "min-max")
    "TEACHERS_PER_SCHOOL": "15-30",
    "STUDENTS_PER_SECTION": "18-32",
    
    # NEW: Ratio Logic
    "SECTIONS_PER_TEACHER_TERM": 5, # How many classes a teacher teaches per term
    
    "SCHOOL_START_YEAR": "2025",
    "NUM_TERMS": 2,
    "INCLUDE_SUMMER": True, # Now triggers the "Overlay" logic
    
    "PROB_FRL": 0.45, "PROB_IEP": 0.12, "PROB_ELL": 0.10,
    "PROB_504": 0.05, "PROB_GIFTED": 0.08, "PROB_DISABILITY": 0.11,
    
    "DO_EXTENSIONS": False, "DO_CONTACTS": True,
    "DO_RESOURCES": False, "DO_ATTENDANCE": False,
    "ATT_START_DATE": "2025-09-01", "ATT_DAYS": 5, "ATT_MODE": "Section" 
}

# ==========================================
# 2. CONSTANTS & HELPER FUNCTIONS
# ==========================================
GENERIC_DISTRICT_NAMES = [ "MapleValley", "OakRiver", "SummitHeights", "PineCreek", "LibertyUnion", "Heritage", "PioneerValley", "GrandView", "Clearwater", "HopeSprings", "NorthStar", "GoldenPlains", "SilverLake", "WillowCreek", "Unity", "CedarRidge" ]
random.shuffle(GENERIC_DISTRICT_NAMES)

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

def get_hex_id(length=6): return uuid.uuid4().hex[:length]
def get_sequential_id(base, counter): return str(base + counter)
def clean_phone(): return re.sub("[^0-9]", "", fake.phone_number())[:10]

# --- NEW: Range Parser ---
def parse_count(val_input):
    """Parses '15-50' into a random int, or '20' into a fixed int."""
    val_str = str(val_input).strip()
    if "-" in val_str:
        try:
            low, high = map(int, val_str.split("-"))
            return random.randint(low, high)
        except:
            return 10 # Fallback
    else:
        return int(val_str)

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
    # CORE TERMS ONLY (Summer is separate now)
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

# ==========================================
# 3. USER INPUT LOGIC
# ==========================================
console.rule("[bold green]Clever Demo District Generator (v9.0 - Variance & Ratios)[/bold green]")

if Confirm.ask(f"Apply ALL default settings?", default=False):
    ID_MODE, OUTPUT_FORMAT, OUTPUT_SCHEMA = DEFAULTS["ID_MODE"], DEFAULTS["OUTPUT_FORMAT"], DEFAULTS["OUTPUT_SCHEMA"]
    EMAIL_DOMAIN, USERNAME_FMT = DEFAULTS["EMAIL_DOMAIN"], DEFAULTS["USERNAME_FMT"]
    NUM_DISTRICTS, SCHOOLS_PER_DISTRICT = DEFAULTS["NUM_DISTRICTS"], DEFAULTS["SCHOOLS_PER_DISTRICT"]
    
    # Range Defaults
    TEACHERS_INPUT, STUDENTS_INPUT = DEFAULTS["TEACHERS_PER_SCHOOL"], DEFAULTS["STUDENTS_PER_SECTION"]
    SECTIONS_PER_TEACHER_TERM = DEFAULTS["SECTIONS_PER_TEACHER_TERM"]
    
    SCHOOL_START_YEAR, NUM_TERMS, INCLUDE_SUMMER = DEFAULTS["SCHOOL_START_YEAR"], DEFAULTS["NUM_TERMS"], DEFAULTS["INCLUDE_SUMMER"]
    PROB_FRL, PROB_IEP, PROB_ELL, PROB_504, PROB_GIFTED, PROB_DISABILITY = DEFAULTS["PROB_FRL"], DEFAULTS["PROB_IEP"], DEFAULTS["PROB_ELL"], DEFAULTS["PROB_504"], DEFAULTS["PROB_GIFTED"], DEFAULTS["PROB_DISABILITY"]
    DO_EXTENSIONS, DO_CONTACTS, DO_RESOURCES, DO_ATTENDANCE = DEFAULTS["DO_EXTENSIONS"], DEFAULTS["DO_CONTACTS"], DEFAULTS["DO_RESOURCES"], DEFAULTS["DO_ATTENDANCE"]
    ATT_CONFIG = {'start_date': DEFAULTS["ATT_START_DATE"], 'days': DEFAULTS["ATT_DAYS"], 'mode': DEFAULTS["ATT_MODE"]}
else:
    ID_MODE = Prompt.ask("Select ID Mode", choices=["sequential", "alphanumeric"], default=DEFAULTS["ID_MODE"])
    OUTPUT_SCHEMA = Prompt.ask("Output Schema", choices=["standard", "anyschool", "both"], default="standard")
    OUTPUT_FORMAT = Prompt.ask("Output Format", choices=["csv", "json", "both"], default="csv")
    EMAIL_DOMAIN = Prompt.ask("Custom Email Domain (Leave blank for default)", default="")
    USERNAME_FMT = Prompt.ask("Username Format", choices=["first.last", "f.last", "f_last", "flast"], default="first.last")
    NUM_DISTRICTS = IntPrompt.ask("Districts", default=DEFAULTS["NUM_DISTRICTS"])
    SCHOOLS_PER_DISTRICT = IntPrompt.ask("Schools per District", default=DEFAULTS["SCHOOLS_PER_DISTRICT"])

    console.print("\n[bold cyan]-- Ranges & Ratios --[/bold cyan]")
    # NEW PROMPTS FOR RANGES
    TEACHERS_INPUT = Prompt.ask("Teachers per School (e.g. '25' or '15-40')", default=str(DEFAULTS["TEACHERS_PER_SCHOOL"]))
    STUDENTS_INPUT = Prompt.ask("Students per Section (e.g. '20' or '15-30')", default=str(DEFAULTS["STUDENTS_PER_SECTION"]))
    SECTIONS_PER_TEACHER_TERM = IntPrompt.ask("Sections per Teacher (per Term)", default=DEFAULTS["SECTIONS_PER_TEACHER_TERM"])

    SCHOOL_START_YEAR = Prompt.ask("School Start Year (YYYY)", default=DEFAULTS["SCHOOL_START_YEAR"])
    NUM_TERMS = IntPrompt.ask("Terms per Year", choices=["2", "3", "4"], default=DEFAULTS["NUM_TERMS"])
    INCLUDE_SUMMER = Confirm.ask("Include Summer Session (35% Teacher / 30% Student coverage)?", default=DEFAULTS["INCLUDE_SUMMER"])
    
    # Demographics Block (Simplified)
    console.print("\n[bold yellow]-- Demographics --[/bold yellow]")
    if Confirm.ask("Use default demographic probabilities?", default=True):
        PROB_FRL, PROB_IEP, PROB_ELL, PROB_504, PROB_GIFTED, PROB_DISABILITY = DEFAULTS["PROB_FRL"], DEFAULTS["PROB_IEP"], DEFAULTS["PROB_ELL"], DEFAULTS["PROB_504"], DEFAULTS["PROB_GIFTED"], DEFAULTS["PROB_DISABILITY"]
    else:
        PROB_FRL = FloatPrompt.ask("Prob. FRL", default=DEFAULTS["PROB_FRL"])
        PROB_IEP = FloatPrompt.ask("Prob. IEP", default=DEFAULTS["PROB_IEP"])
        PROB_ELL = FloatPrompt.ask("Prob. ELL", default=DEFAULTS["PROB_ELL"])
        PROB_504 = FloatPrompt.ask("Prob. 504", default=DEFAULTS["PROB_504"])
        PROB_GIFTED = FloatPrompt.ask("Prob. Gifted", default=DEFAULTS["PROB_GIFTED"])
        PROB_DISABILITY = FloatPrompt.ask("Prob. Disability", default=DEFAULTS["PROB_DISABILITY"])
        
    # Supplemental
    DO_EXTENSIONS = Confirm.ask("Add Extensions?", default=DEFAULTS["DO_EXTENSIONS"])
    DO_CONTACTS = Confirm.ask("Add Contacts?", default=DEFAULTS["DO_CONTACTS"])
    DO_RESOURCES = Confirm.ask("Add Resources?", default=DEFAULTS["DO_RESOURCES"])
    DO_ATTENDANCE = Confirm.ask("Add Attendance?", default=DEFAULTS["DO_ATTENDANCE"])
    ATT_CONFIG = {'start_date': "2025-01-01", 'days': 0, 'mode': "Section"}
    if DO_ATTENDANCE:
        ATT_CONFIG['start_date'] = Prompt.ask("Start Date", default=DEFAULTS["ATT_START_DATE"])
        ATT_CONFIG['days'] = IntPrompt.ask("Days", default=DEFAULTS["ATT_DAYS"])
        ATT_CONFIG['mode'] = Prompt.ask("Mode", choices=["Daily", "Section"], default=DEFAULTS["ATT_MODE"])

if not Confirm.ask("Ready to generate?", default=True): exit()

# ==========================================
# 4. MAIN LOGIC
# ==========================================
base_output_dir = 'district_data_output'
CORE_TERMS = generate_term_schedule(SCHOOL_START_YEAR, NUM_TERMS)
console.print(f"\n[yellow]Core Logic:[/yellow] {len(CORE_TERMS)} terms. [cyan]Summer Overlay:[/cyan] {'Enabled' if INCLUDE_SUMMER else 'Disabled'}")

with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn(), console=console) as progress:
    main_task = progress.add_task("[green]Initializing...", total=NUM_DISTRICTS)

    for i in range(NUM_DISTRICTS):
        dist_name = GENERIC_DISTRICT_NAMES[i % len(GENERIC_DISTRICT_NAMES)]
        progress.update(main_task, description=f"[green]Generating {dist_name}...[/green]")
        
        email_domain = EMAIL_DOMAIN if EMAIL_DOMAIN else f"{dist_name.lower()}.k12.edu"
        state_key = STATE_KEYS[i % len(STATE_KEYS)]
        state_name, state_abbr = STATE_MAPPINGS[state_key]
        district_prefix = str(10 + i) 
        base_id_seq = (i + 1) * 100000 

        schools_data, teachers_data, staff_data = [], [], []
        students_data, sections_data, enrollments_data = [], [], []
        
        # --- SCHOOL LOOP ---
        for s_idx in range(SCHOOLS_PER_DISTRICT):
            if ID_MODE == 'alphanumeric': school_id = get_hex_id(6)
            else: school_id = get_sequential_id(base_id_seq, s_idx * 10000) # Spacing out IDs
            
            school_type = random.choice(['Elementary', 'Middle', 'High', 'Academy'])
            school_code = f"{s_idx + 1:02d}"
            if 'Elementary' in school_type: low, high = 'KG', '5'
            elif 'Middle' in school_type: low, high = '6', '8'
            elif 'High' in school_type: low, high = '9', '12'
            else: low, high = 'KG', '12'
            
            valid_locations = REAL_LOCATIONS.get(state_abbr, [("City", "000")])
            city_name, zip_prefix = random.choice(valid_locations)
            
            schools_data.append({
                "School_id": school_id, "School_name": f"{fake.last_name()} {school_type}",
                "School_number": school_code, "Low_grade": low, "High_grade": high,
                "Principal": fake.name(), "Principal_email": f"principal.{school_id}@{email_domain}",
                "School_address": fake.street_address(), "School_city": city_name, "School_state": state_abbr, "School_zip": f"{zip_prefix}{random.randint(10, 99)}", "School_phone": fake.phone_number()
            })

            # --- TEACHER GENERATION (Using Range) ---
            num_teachers = parse_count(TEACHERS_INPUT) # e.g. Randomly 18 or 42
            school_teacher_ids = []
            
            for t_idx in range(num_teachers):
                t_id = get_hex_id(7) if ID_MODE == 'alphanumeric' else get_sequential_id(base_id_seq, (s_idx * 1000) + t_idx)
                f, l = fake.first_name(), fake.last_name()
                username, email = generate_email_username(f, l, email_domain, USERNAME_FMT)
                teachers_data.append({
                    "School_id": school_id, "Teacher_id": t_id, "Teacher_number": t_id[:8], "State_teacher_id": f"{state_abbr}-{t_id[:8]}",
                    "Teacher_email": email, "Username": username, "First_name": f, "Last_name": l, "Title": "Teacher"
                })
                school_teacher_ids.append(t_id)

            # --- STAFF GENERATION ---
            for st_idx in range(2):
                st_id = get_hex_id(7) if ID_MODE == 'alphanumeric' else get_sequential_id(base_id_seq, 90000 + (s_idx*10) + st_idx)
                f, l = fake.first_name(), fake.last_name()
                username, email = generate_email_username(f, l, email_domain, USERNAME_FMT)
                staff_data.append({
                    "School_id": school_id, "Staff_id": st_id, "Staff_email": email, "First_name": f, "Last_name": l, "Department": "Admin", "Title": "Staff"
                })

            # --- PASS 1: CORE SECTIONS (Ratio Based) ---
            # Instead of Loop Range(Sections), we Loop Teachers -> Term -> Ratio
            grade_list = [str(g) if g > 0 else 'KG' for g in range(int(low) if low.isdigit() else 0, (int(high) if high.isdigit() else 12) + 1)]
            
            school_section_ids = [] # Track for student enrollment

            for t_id in school_teacher_ids:
                for term in CORE_TERMS:
                    for _ in range(SECTIONS_PER_TEACHER_TERM):
                        sec_id = get_hex_id(8) if ID_MODE == 'alphanumeric' else f"SEC-{uuid.uuid4().hex[:8]}"
                        s_grade = random.choice(grade_list)
                        s_subj = random.choice(['Math', 'Science', 'ELA', 'History', 'Art', 'PE'])
                        
                        sections_data.append({
                            "School_id": school_id, "Section_id": sec_id, "Teacher_id": t_id, "Teacher_2_id": "",
                            "Name": f"{s_grade} - {s_subj}", "Grade": s_grade, "Subject": s_subj,
                            "Term_name": term["Term_name"], "Term_start": term["Term_start"], "Term_end": term["Term_end"]
                        })
                        school_section_ids.append({"id": sec_id, "grade": s_grade})

            # --- STUDENT GENERATION & CORE ENROLLMENT ---
            # We need enough students to fill these sections roughly.
            # Estimate: Total Sections * Students_Per_Section_Avg / Classes_Per_Student (assume 6)
            # Or just user simpler logic: Create N students per section capacity
            # Simplified: Iterate sections, fill with NEW or EXISTING students?
            # Better: Create a pool of students for the school first.
            
            avg_sec_size = parse_count(STUDENTS_INPUT)
            # Total Enrollment needs to support the sections. 
            # If we have 100 sections, and each student takes ~6 classes, and sections size is ~25.
            # (100 * 25) / 6 = ~416 students needed.
            estimated_students = int((len(school_section_ids) * avg_sec_size) / SECTIONS_PER_TEACHER_TERM)
            
            school_student_objs = []
            for stu_idx in range(estimated_students):
                stu_id = get_hex_id(6) if ID_MODE == 'alphanumeric' else get_sequential_id(base_id_seq, 200000 + (s_idx * 5000) + stu_idx)
                f, l = fake.first_name(), fake.last_name()
                username, email = generate_email_username(f, l, email_domain, USERNAME_FMT)
                s_grade = random.choice(grade_list)
                
                # ... (Demographics generation - compressed for brevity) ...
                has_disability = "Y" if random.random() < PROB_DISABILITY else "N"
                dis_code, dis_type = ("", "")
                if has_disability == "Y":
                    c = random.choice(DISABILITY_CODES)
                    dis_code, dis_type = c, DISABILITY_MAP[c]
                
                stu_obj = {
                    "School_id": school_id, "Student_id": stu_id, "Student_number": stu_id[:8], "State_id": f"{state_abbr}-{stu_id[:8]}",
                    "Last_name": l, "First_name": f, "Grade": s_grade, "Gender": random.choice(['M', 'F']),
                    "DOB": generate_dob(s_grade), "Email_address": email, "Username": username,
                    "Race": random.choices(CLEVER_RACE_VALUES, weights=RACE_WEIGHTS)[0],
                    "Home_language": random.choices(LANG_KEYS, weights=LANG_WEIGHTS)[0],
                    "IEP_status": "Y" if random.random() < PROB_IEP else "N", "FRL_status": "Y" if random.random() < PROB_FRL else "N",
                    "ELL_status": "Y" if random.random() < PROB_ELL else "N", "Section_504_status": "Y" if random.random() < PROB_504 else "N",
                    "Gifted_status": "Y" if random.random() < PROB_GIFTED else "N", "Disability_status": has_disability, "Disability_type": dis_type, "Disability_code": dis_code
                }
                if DO_EXTENSIONS: stu_obj['ext.locker_number'], stu_obj['ext.bus_route'] = random.randint(100, 9999), random.choice(['Route A', 'Route B'])
                
                school_student_objs.append(stu_obj)
                
                # Add Contacts
                if DO_CONTACTS:
                    hh = generate_household_contacts(l, email_domain)
                    for c in hh:
                        r = stu_obj.copy()
                        r.update(c)
                        students_data.append(r)
                else:
                    students_data.append(stu_obj)

            # --- CORE ENROLLMENT LOGIC ---
            # Randomly enroll students in sections matching their grade
            # Each student gets enrolled in SECTIONS_PER_TEACHER_TERM * NUM_TERMS (roughly)
            # Actually, simpler: Iterate Sections, fill with random students of that grade.
            
            students_by_grade = {g: [s for s in school_student_objs if s['Grade'] == g] for g in grade_list}
            
            for sec in school_section_ids:
                target_grade = sec['grade']
                available_students = students_by_grade.get(target_grade, [])
                if not available_students: continue
                
                # Random count for this specific section
                count = parse_count(STUDENTS_INPUT)
                selected = random.sample(available_students, k=min(count, len(available_students)))
                
                for s in selected:
                    enrollments_data.append({"School_id": school_id, "Section_id": sec['id'], "Student_id": s['Student_id']})

            # --- PASS 2: SUMMER OVERLAY ---
            if INCLUDE_SUMMER:
                summer_term = generate_summer_term(SCHOOL_START_YEAR)
                
                # 1. Select 35% of Teachers
                k_teach = int(len(school_teacher_ids) * 0.35)
                summer_teachers = random.sample(school_teacher_ids, k=max(1, k_teach))
                
                summer_sections = []
                # Create 1-2 sections per summer teacher
                for st_id in summer_teachers:
                    for _ in range(random.randint(1,2)):
                        sec_id = f"SUM-{uuid.uuid4().hex[:6]}"
                        s_grade = random.choice(grade_list)
                        s_subj = "Summer " + random.choice(['Math', 'Reading', 'Credit Recovery'])
                        sections_data.append({
                            "School_id": school_id, "Section_id": sec_id, "Teacher_id": st_id, "Teacher_2_id": "",
                            "Name": f"{s_grade} - {s_subj}", "Grade": s_grade, "Subject": s_subj,
                            "Term_name": summer_term["Term_name"], "Term_start": summer_term["Term_start"], "Term_end": summer_term["Term_end"]
                        })
                        summer_sections.append({"id": sec_id, "grade": s_grade})

                # 2. Select 30% of Students
                k_stu = int(len(school_student_objs) * 0.30)
                summer_students = random.sample(school_student_objs, k=max(1, k_stu))
                summer_students_by_grade = {g: [s for s in summer_students if s['Grade'] == g] for g in grade_list}

                # 3. Enroll
                for sec in summer_sections:
                    target_grade = sec['grade']
                    avail = summer_students_by_grade.get(target_grade, [])
                    if not avail: continue
                    # Summer classes usually smaller, say 10-20
                    count = random.randint(10, 20)
                    selected = random.sample(avail, k=min(count, len(avail)))
                    for s in selected:
                        enrollments_data.append({"School_id": school_id, "Section_id": sec['id'], "Student_id": s['Student_id']})

        # E. ADMIN (District Level)
        if schools_data:
            admin_id = get_hex_id(7) if ID_MODE == 'alphanumeric' else str(base_id_seq + 99999)
            staff_data.insert(0, { "School_id": schools_data[0]['School_id'], "Staff_id": admin_id, "Staff_email": f"admin@{email_domain}", "First_name": "System", "Last_name": "Admin", "Department": "Central", "Title": "Admin" })

        # --- SAVING (anyschool Transformer included) ---
        def transform_to_anyschool(students, teachers, staff, sections, enrollments, schools):
            school_map = {s['School_id']: {'name': s['School_name'], 'number': s['School_number']} for s in schools}
            def fmt_date(d):
                try: return datetime.datetime.strptime(d, "%Y-%m-%d").strftime("%m/%d/%Y")
                except: return d
            users_out, sections_out = [], []
            seen_students = set()
            
            # Users
            for s in students:
                if s['Student_id'] in seen_students: continue
                seen_students.add(s['Student_id'])
                users_out.append({"School_name": school_map[s['School_id']]['name'], "User_type": "student", "User_id": s['Student_id'], "First_name": s['First_name'], "Last_name": s['Last_name'], "Email": s['Email_address'], "Username": s.get('Username', ''), "Grade": s['Grade'], "DOB": fmt_date(s['DOB'])})
            for t in teachers:
                users_out.append({"School_name": school_map[t['School_id']]['name'], "User_type": "teacher", "User_id": t['Teacher_id'], "First_name": t['First_name'], "Last_name": t['Last_name'], "Email": t['Teacher_email'], "Username": t.get('Username', ''), "Grade": "", "DOB": ""})
            for st in staff:
                users_out.append({"School_name": school_map[st['School_id']]['name'], "User_type": "staff", "User_id": st['Staff_id'], "First_name": st['First_name'], "Last_name": st['Last_name'], "Email": st['Staff_email'], "Username": st.get('Staff_email', '').split('@')[0], "Grade": "", "DOB": ""})
            
            # Sections (Flattened)
            sec_lookup = {x['Section_id']: x for x in sections}
            for e in enrollments:
                sd = sec_lookup.get(e['Section_id'])
                if not sd: continue
                sections_out.append({"School_name": school_map[e['School_id']]['name'], "Section_id": e['Section_id'], "User_id": e['Student_id'], "Teacher_id": sd['Teacher_id'], "School_number": school_map[e['School_id']]['number'], "Subject": sd['Subject'], "Period": "1", "Section_name": sd['Name']})
            return users_out, sections_out

        def save_data(data, fname, out_dir, fmt):
            if not data: return
            df = pd.DataFrame(data)
            if fmt in ['csv', 'both']: df.to_csv(os.path.join(out_dir, f"{fname}.csv"), index=False)
            if fmt in ['json', 'both']: df.to_json(os.path.join(out_dir, f"{fname}.json"), orient='records', indent=4)

        progress.update(main_task, description=f"[yellow]Saving {dist_name}...[/yellow]")
        out_dir = os.path.join(base_output_dir, f"{dist_name}_Data")
        os.makedirs(out_dir, exist_ok=True)
        
        if OUTPUT_SCHEMA in ["standard", "both"]:
            d = os.path.join(out_dir, "standard") if OUTPUT_SCHEMA == "both" else out_dir
            os.makedirs(d, exist_ok=True)
            for k, v in [("schools", schools_data), ("teachers", teachers_data), ("staff", staff_data), ("students", students_data), ("sections", sections_data), ("enrollments", enrollments_data)]:
                save_data(v, k, d, OUTPUT_FORMAT)
                
        if OUTPUT_SCHEMA in ["anyschool", "both"]:
            d = os.path.join(out_dir, "anyschool") if OUTPUT_SCHEMA == "both" else out_dir
            os.makedirs(d, exist_ok=True)
            u_csv, s_csv = transform_to_anyschool(students_data, teachers_data, staff_data, sections_data, enrollments_data, schools_data)
            save_data(u_csv, "users", d, OUTPUT_FORMAT)
            save_data(s_csv, "sections", d, OUTPUT_FORMAT)
        
        progress.advance(main_task)
        console.print(f":white_check_mark: [green]{dist_name} Complete[/green]")

console.print("\n[bold blue]Generation Complete![/bold blue]")