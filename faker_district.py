import os
import random
import uuid
import datetime
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
    "NUM_DISTRICTS": 1,
    "SCHOOLS_PER_DISTRICT": 5,
    "TEACHERS_PER_SCHOOL": 15,
    
    # Recommendation: Set SECTIONS_PER_SCHOOL to Teachers * Number of desired terms.
    # If you want Summer data, you need to budget "extra" sections in your configuration to push the rotation far enough to hit that Summer slot.
    # Ex: If using Quarters (4 terms) and 15 teachers per school, set this to at least 60 (4 per teacher, 1 per term).
    
    # The default ratio is set for semesters: 2 sections for each term + one summer section for each teacher.
    
    # General rule of thumb: If adding summer terms, add additional sections per school at a ratio of 1:1 for sections:teachers per school.
    "SECTIONS_PER_SCHOOL": 75,
    "STUDENTS_PER_SECTION": 20,
    
    # Term Configuration
    "SCHOOL_START_YEAR": "2025",
    "NUM_TERMS": 2,               # 2=Semester, 3=Trimester, 4=Quarter
    "INCLUDE_SUMMER": True,
    
    # Demographics
    "PROB_FRL": 0.45, "PROB_IEP": 0.12, "PROB_ELL": 0.10,
    "PROB_504": 0.05, "PROB_GIFTED": 0.08, "PROB_DISABILITY": 0.11,
    
    # Toggles
    "DO_EXTENSIONS": False,
    "DO_RESOURCES": False,
    "DO_ATTENDANCE": False,
    
    # Attendance Context (Still needed if attendance is on)
    "ATT_START_DATE": "2025-09-01", 
    "ATT_DAYS": 5,
    "ATT_MODE": "Section" 
}

# ==========================================
# 2. CONSTANTS & MAPPINGS
# ==========================================
GENERIC_DISTRICT_NAMES = [
    "MapleValley", "OakRiver", "SummitHeights", "PineCreek", 
    "LibertyUnion", "Heritage", "PioneerValley", "GrandView", 
    "Clearwater", "HopeSprings", "NorthStar", "GoldenPlains",
    "SilverLake", "WillowCreek", "Unity", "CedarRidge"
]
random.shuffle(GENERIC_DISTRICT_NAMES)

STATE_MAPPINGS = {
    "C4a": ("California", "CA"), "T3x": ("Texas", "TX"), "N3y": ("New York", "NY"),
    "F1a": ("Florida", "FL"), "W2a": ("Washington", "WA"), "I1l": ("Illinois", "IL"),
    "C0l": ("Colorado", "CO"), "A7z": ("Arizona", "AZ"), "G4a": ("Georgia", "GA"),
    "M4a": ("Massachusetts", "MA")
}
STATE_KEYS = list(STATE_MAPPINGS.keys())

REAL_LOCATIONS = {
    "CA": [("San Francisco", "941"), ("Los Angeles", "900"), ("San Diego", "921"), ("Sacramento", "958"), ("Fresno", "937")],
    "TX": [("Austin", "787"), ("Houston", "770"), ("Dallas", "752"), ("San Antonio", "782"), ("Fort Worth", "761")],
    "NY": [("New York", "100"), ("Brooklyn", "112"), ("Bronx", "104"), ("Buffalo", "142"), ("Albany", "122")],
    "FL": [("Miami", "331"), ("Orlando", "328"), ("Tampa", "336"), ("Jacksonville", "322"), ("Tallahassee", "323")],
    "WA": [("Seattle", "981"), ("Spokane", "992"), ("Tacoma", "984"), ("Vancouver", "986"), ("Bellevue", "980")],
    "IL": [("Chicago", "606"), ("Springfield", "627"), ("Peoria", "616"), ("Naperville", "605"), ("Rockford", "611")],
    "CO": [("Denver", "802"), ("Colorado Springs", "809"), ("Boulder", "803"), ("Aurora", "800"), ("Fort Collins", "805")],
    "AZ": [("Phoenix", "850"), ("Tucson", "857"), ("Mesa", "852"), ("Scottsdale", "852"), ("Chandler", "852")],
    "GA": [("Atlanta", "303"), ("Savannah", "314"), ("Augusta", "309"), ("Athens", "306"), ("Macon", "312")],
    "MA": [("Boston", "021"), ("Worcester", "016"), ("Springfield", "011"), ("Cambridge", "021"), ("Lowell", "018")]
}

CLEVER_RACE_VALUES = ["White", "Black or African American", "Asian", "American Indian or Alaska Native", "Native Hawaiian or Other Pacific Islander", "Two or more races", "Unknown"]
RACE_WEIGHTS = [0.50, 0.15, 0.06, 0.02, 0.01, 0.06, 0.20]

LANGUAGE_MAP = { "eng": 0.70, "spa": 0.20, "vie": 0.03, "zho": 0.02, "ara": 0.02, "tgl": 0.01, "rus": 0.01, "som": 0.01 }
LANG_KEYS = list(LANGUAGE_MAP.keys())
LANG_WEIGHTS = list(LANGUAGE_MAP.values())

DISABILITY_MAP = { "AUT": "Autism", "DB": "Deaf-blindness", "DD": "Developmental delay", "EMN": "Emotional disturbance", "HI": "Hearing impairment", "ID": "Intellectual Disability", "MD": "Multiple disabilities", "OI": "Orthopedic impairment", "OHI": "Other health impairment", "SLD": "Specific learning disability", "SLI": "Speech or language impairment", "TBI": "Traumatic brain injury", "VI": "Visual impairment" }
DISABILITY_CODES = list(DISABILITY_MAP.keys())

# ==========================================
# 3. USER INPUT LOGIC
# ==========================================
console.rule("[bold green]Unified District Generator (v4.0 - Dynamic Terms)[/bold green]")

USE_DEFAULTS = Confirm.ask(f"Apply default settings?", default=False)

if USE_DEFAULTS:
    ID_MODE = DEFAULTS["ID_MODE"]
    NUM_DISTRICTS = DEFAULTS["NUM_DISTRICTS"]
    SCHOOLS_PER_DISTRICT = DEFAULTS["SCHOOLS_PER_DISTRICT"]
    TEACHERS_PER_SCHOOL = DEFAULTS["TEACHERS_PER_SCHOOL"]
    SECTIONS_PER_SCHOOL = DEFAULTS["SECTIONS_PER_SCHOOL"]
    STUDENTS_PER_SECTION = DEFAULTS["STUDENTS_PER_SECTION"]
    
    # Term Defaults
    SCHOOL_START_YEAR = DEFAULTS["SCHOOL_START_YEAR"]
    NUM_TERMS = DEFAULTS["NUM_TERMS"]
    INCLUDE_SUMMER = DEFAULTS["INCLUDE_SUMMER"]
    
    PROB_FRL = DEFAULTS["PROB_FRL"]
    PROB_IEP = DEFAULTS["PROB_IEP"]
    PROB_ELL = DEFAULTS["PROB_ELL"]
    PROB_504 = DEFAULTS["PROB_504"]
    PROB_GIFTED = DEFAULTS["PROB_GIFTED"]
    PROB_DISABILITY = DEFAULTS["PROB_DISABILITY"]
    
    DO_EXTENSIONS = DEFAULTS["DO_EXTENSIONS"]
    DO_RESOURCES = DEFAULTS["DO_RESOURCES"]
    DO_ATTENDANCE = DEFAULTS["DO_ATTENDANCE"]
    
    ATT_CONFIG = {'start_date': DEFAULTS["ATT_START_DATE"], 'days': DEFAULTS["ATT_DAYS"], 'mode': DEFAULTS["ATT_MODE"]}
    console.print("[yellow]Defaults loaded![/yellow]")
else:
    ID_MODE = Prompt.ask("Select ID Mode", choices=["sequential", "alphanumeric"], default=DEFAULTS["ID_MODE"])
    NUM_DISTRICTS = IntPrompt.ask("Districts", default=DEFAULTS["NUM_DISTRICTS"])
    SCHOOLS_PER_DISTRICT = IntPrompt.ask("Schools per District", default=DEFAULTS["SCHOOLS_PER_DISTRICT"])
    TEACHERS_PER_SCHOOL = IntPrompt.ask("Teachers per School", default=DEFAULTS["TEACHERS_PER_SCHOOL"])
    SECTIONS_PER_SCHOOL = IntPrompt.ask("Sections per School", default=DEFAULTS["SECTIONS_PER_SCHOOL"])
    STUDENTS_PER_SECTION = IntPrompt.ask("Students per Section", default=DEFAULTS["STUDENTS_PER_SECTION"])

    console.print("\n[bold cyan]-- Term Configuration --[/bold cyan]")
    SCHOOL_START_YEAR = Prompt.ask("School Start Year (YYYY)", default=DEFAULTS["SCHOOL_START_YEAR"])
    NUM_TERMS = IntPrompt.ask("Terms per Year (2=Sem, 3=Tri, 4=Qtr)", choices=["2", "3", "4"], default=DEFAULTS["NUM_TERMS"])
    INCLUDE_SUMMER = Confirm.ask("Include Summer Session?", default=DEFAULTS["INCLUDE_SUMMER"])

    console.print("\n[bold yellow]-- Demographics --[/bold yellow]")
    PROB_FRL = FloatPrompt.ask("Prob. FRL", default=DEFAULTS["PROB_FRL"])
    PROB_IEP = FloatPrompt.ask("Prob. IEP", default=DEFAULTS["PROB_IEP"])
    PROB_ELL = FloatPrompt.ask("Prob. ELL", default=DEFAULTS["PROB_ELL"])
    PROB_504 = FloatPrompt.ask("Prob. 504", default=DEFAULTS["PROB_504"])
    PROB_GIFTED = FloatPrompt.ask("Prob. Gifted", default=DEFAULTS["PROB_GIFTED"])
    PROB_DISABILITY = FloatPrompt.ask("Prob. Disability", default=DEFAULTS["PROB_DISABILITY"])

    console.print("\n[bold cyan]-- Supplemental Data --[/bold cyan]")
    DO_EXTENSIONS = Confirm.ask("Add Extension Fields?", default=DEFAULTS["DO_EXTENSIONS"])
    DO_RESOURCES = Confirm.ask("Generate Resources.csv?", default=DEFAULTS["DO_RESOURCES"])
    DO_ATTENDANCE = Confirm.ask("Generate Attendance.csv?", default=DEFAULTS["DO_ATTENDANCE"])

    ATT_CONFIG = {}
    if DO_ATTENDANCE:
        ATT_CONFIG['start_date'] = Prompt.ask("   Attendance Start Date", default=DEFAULTS["ATT_START_DATE"])
        ATT_CONFIG['days'] = IntPrompt.ask("   Days to Generate", default=DEFAULTS["ATT_DAYS"])
        ATT_CONFIG['mode'] = Prompt.ask("   Mode", choices=["Daily", "Section"], default=DEFAULTS["ATT_MODE"])
    else:
        ATT_CONFIG = {'start_date': "2025-01-01", 'days': 0, 'mode': "Section"}

if not Confirm.ask("Ready to generate?", default=True): exit()

# ==========================================
# 4. HELPER FUNCTIONS
# ==========================================
def get_hex_id(length=6): return uuid.uuid4().hex[:length]
def get_sequential_id(base, counter): return str(base + counter)

def generate_dob(grade):
    current_year = datetime.date.today().year
    grade_map = {'PK':4,'KG':5,'1':6,'2':7,'3':8,'4':9,'5':10,'6':11,'7':12,'8':13,'9':14,'10':15,'11':16,'12':17}
    target_age = grade_map.get(grade, 10)
    birth_year = current_year - target_age
    return fake.date_between(start_date=datetime.date(birth_year,1,1), end_date=datetime.date(birth_year,12,31)).strftime('%Y-%m-%d')

def generate_date_range(start_str, days):
    dates = []
    current = datetime.datetime.strptime(start_str, "%Y-%m-%d").date()
    while len(dates) < days:
        if current.weekday() < 5: dates.append(current)
        current += datetime.timedelta(days=1)
    return dates

def generate_term_schedule(anchor_year_str, num_terms, include_summer):
    """
    Generates a list of term dictionaries (cycle) based on config.
    """
    y_start = int(anchor_year_str)
    y_end = y_start + 1
    terms = []

    # 1. Core Terms
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

    # 2. Summer Term
    if include_summer:
        terms.append({"Term_name": f"Summer {y_end}", "Term_start": f"{y_end}-06-01", "Term_end": f"{y_end}-07-30"})
        
    return terms

# ==========================================
# 5. MAIN GENERATION LOOP
# ==========================================
base_output_dir = 'district_data_output'

# Generate the global term cycle based on user config
TERM_CYCLE = generate_term_schedule(SCHOOL_START_YEAR, NUM_TERMS, INCLUDE_SUMMER)
console.print(f"\n[yellow]Term Logic Active:[/yellow] {len(TERM_CYCLE)} terms in rotation.")

with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn(), console=console) as progress:
    main_task = progress.add_task("[green]Initializing...", total=NUM_DISTRICTS)

    for i in range(NUM_DISTRICTS):
        # --- PHASE 1: CORE STRUCTURE ---
        dist_name = GENERIC_DISTRICT_NAMES[i % len(GENERIC_DISTRICT_NAMES)]
        progress.update(main_task, description=f"[green]Generating {dist_name}...[/green]")
        
        state_key = STATE_KEYS[i % len(STATE_KEYS)]
        state_name, state_abbr = STATE_MAPPINGS[state_key]
        email_domain = f"{dist_name.lower()}.k12.edu"
        district_prefix = str(10 + i) 
        base_id_seq = (i + 1) * 100000 

        schools_data, teachers_data, staff_data = [], [], []
        students_data, sections_data, enrollments_data = [], [], []

        # A. SCHOOLS
        for s_idx in range(SCHOOLS_PER_DISTRICT):
            if ID_MODE == 'alphanumeric': school_id = get_hex_id(random.choice([5, 6]))
            else: school_id = get_sequential_id(base_id_seq, s_idx * 100)

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
                "School_address": fake.street_address(), "School_city": city_name,
                "School_state": state_abbr, "School_zip": f"{zip_prefix}{random.randint(10, 99)}",
                "School_phone": fake.phone_number()
            })

            # B. TEACHERS
            school_teacher_ids = []
            for t_idx in range(TEACHERS_PER_SCHOOL):
                if ID_MODE == 'alphanumeric':
                    t_id = get_hex_id(7)
                    t_num = f"T-{random.randint(100000, 999999)}"
                    st_id = f"{state_abbr}-{t_num}"
                else:
                    t_id = get_sequential_id(base_id_seq, (s_idx * 1000) + t_idx)
                    t_num, st_id = t_id, t_id

                f, l = fake.first_name(), fake.last_name()
                teachers_data.append({
                    "School_id": school_id, "Teacher_id": t_id, "Teacher_number": t_num, "State_teacher_id": st_id,
                    "Teacher_email": f"{f[0].lower()}{l.lower()}@{email_domain}", "First_name": f, "Last_name": l, "Title": "Teacher"
                })
                school_teacher_ids.append(t_id)

            # C. STAFF
            for st_idx in range(2):
                st_id = get_hex_id(7) if ID_MODE == 'alphanumeric' else get_sequential_id(base_id_seq, 9000 + st_idx)
                f, l = fake.first_name(), fake.last_name()
                staff_data.append({
                    "School_id": school_id, "Staff_id": st_id, "Staff_email": f"{f}.{l}@{email_domain}",
                    "First_name": f, "Last_name": l, "Department": "Admin", "Title": "Staff"
                })

            # D. ROSTERING (With Dynamic Terms)
            grade_list = [str(g) if g > 0 else 'KG' for g in range(int(low) if low.isdigit() else 0, (int(high) if high.isdigit() else 12) + 1)]
            
            # Track teacher assignments for load balancing within this school
            teacher_load_counts = {} 

            for sec_idx in range(SECTIONS_PER_SCHOOL):
                sec_id = get_hex_id(8) if ID_MODE == 'alphanumeric' else get_sequential_id(base_id_seq, 50000 + sec_idx)
                
                # Pick Primary Teacher
                p_teach = random.choice(school_teacher_ids)
                
                # Pick Secondary Teacher (Optional)
                s_teach = random.choice([t for t in school_teacher_ids if t != p_teach]) if sec_idx == 0 else None
                
                # --- TERM ASSIGNMENT LOGIC ---
                # 1. Get current load for this teacher
                current_load = teacher_load_counts.get(p_teach, 0)
                # 2. Determine term index based on modulo
                term_idx = current_load % len(TERM_CYCLE)
                selected_term = TERM_CYCLE[term_idx]
                # 3. Update load count
                teacher_load_counts[p_teach] = current_load + 1
                # -----------------------------

                s_grade = random.choice(grade_list)
                s_subj = random.choice(['Math', 'Science', 'ELA', 'History'])

                sections_data.append({
                    "School_id": school_id, 
                    "Section_id": sec_id, 
                    "Teacher_id": p_teach, 
                    "Teacher_2_id": s_teach,
                    "Name": f"{s_grade} - {s_subj} ({sec_idx+1})", 
                    "Grade": s_grade, 
                    "Subject": s_subj,
                    "Term_name": selected_term["Term_name"],
                    "Term_start": selected_term["Term_start"],
                    "Term_end": selected_term["Term_end"]
                })

                # STUDENTS
                for stu_idx in range(STUDENTS_PER_SECTION):
                    if ID_MODE == 'alphanumeric':
                        stu_id = get_hex_id(6)
                        stu_num = f"{district_prefix}{random.randint(100000, 999999)}"
                        state_id = f"{state_abbr}-{school_code}-{stu_num}"
                    else:
                        stu_id = get_sequential_id(base_id_seq, 200000 + (sec_idx * 100) + stu_idx)
                        stu_num, state_id = stu_id, stu_id

                    # Gender-Aware Name Generation
                    gender_code = random.choice(['M', 'F'])
                    if gender_code == 'M': f = fake.first_name_male()
                    else: f = fake.first_name_female()
                    l = fake.last_name()
                    
                    has_disability = "Y" if random.random() < PROB_DISABILITY else "N"
                    dis_code, dis_type = ("", "")
                    if has_disability == "Y":
                        code = random.choice(DISABILITY_CODES)
                        dis_code, dis_type = code, DISABILITY_MAP[code]

                    student_obj = {
                        "School_id": school_id, "Student_id": stu_id, "Student_number": stu_num, "State_id": state_id,
                        "Last_name": l, "First_name": f, "Grade": s_grade, 
                        "Gender": gender_code,
                        "DOB": generate_dob(s_grade), "Student_email": f"{f[0]}{l}{random.randint(10,99)}@{email_domain}".lower(),
                        "Race": random.choices(CLEVER_RACE_VALUES, weights=RACE_WEIGHTS)[0],
                        "Home_language": random.choices(LANG_KEYS, weights=LANG_WEIGHTS)[0],
                        "IEP_status": "Y" if random.random() < PROB_IEP else "N",
                        "FRL_status": "Y" if random.random() < PROB_FRL else "N",
                        "ELL_status": "Y" if random.random() < PROB_ELL else "N",
                        "Section_504_status": "Y" if random.random() < PROB_504 else "N",
                        "Gifted_status": "Y" if random.random() < PROB_GIFTED else "N",
                        "Disability_status": has_disability, "Disability_type": dis_type, "Disability_code": dis_code
                    }
                    
                    if DO_EXTENSIONS:
                        student_obj['ext.locker_number'] = random.randint(100, 9999)
                        student_obj['ext.bus_route'] = random.choice(['Route A', 'Route B', 'Walk'])

                    students_data.append(student_obj)
                    enrollments_data.append({"School_id": school_id, "Section_id": sec_id, "Student_id": stu_id})

        # E. ADMIN
        if schools_data:
            admin_id = get_hex_id(7) if ID_MODE == 'alphanumeric' else str(base_id_seq + 99999)
            staff_data.insert(0, { "School_id": schools_data[0]['School_id'], "Staff_id": admin_id, "Staff_email": f"admin@{email_domain}", "First_name": "System", "Last_name": "Admin", "Department": "Central", "Title": "Admin" })

        # --- PHASE 2: SUPPLEMENTAL GENERATION ---
        resources_data = []
        attendance_data = []

        if DO_RESOURCES:
            progress.update(main_task, description=f"[cyan]Resources for {dist_name}...[/cyan]")
            library_pool = [
                ("District Math: Algebra I", "student,teacher"), ("District Math: Geometry", "student,teacher"),
                ("Virtual Lab: Biology", "student,teacher"), ("District Digital Library", "student,teacher"),
                ("World Atlas Interactive", "student,teacher"), ("Attendance Dashboard", "teacher")
            ]
            for title, roles in library_pool:
                prefix = title.split(':')[0][:3].upper().replace(" ", "")
                res_id = f"RES-{prefix}-{str(abs(hash(title)))[:4]}"
                resources_data.append({"resource_id": res_id, "title": title, "roles": roles})

        if DO_ATTENDANCE:
            progress.update(main_task, description=f"[cyan]Attendance for {dist_name}...[/cyan]")
            valid_dates = generate_date_range(ATT_CONFIG['start_date'], ATT_CONFIG['days'])
            
            stu_to_sec = {}
            if ATT_CONFIG['mode'] == "Section":
                for row in enrollments_data:
                    sid = row['Student_id']
                    if sid not in stu_to_sec: stu_to_sec[sid] = []
                    stu_to_sec[sid].append(row['Section_id'])
            
            unique_students = {s['Student_id']: s['School_id'] for s in students_data}

            for date_obj in valid_dates:
                date_str = date_obj.strftime("%Y-%m-%d")
                for sid, sch_id in unique_students.items():
                    if ATT_CONFIG['mode'] == "Daily":
                        status = random.choices(["present", "absent", "tardy"], weights=[0.90, 0.05, 0.05])[0]
                        excuse = f"EXC-{random.randint(100,999)}" if status != "present" else ""
                        attendance_data.append({
                            "sis_id": f"att-{uuid.uuid4().hex[:10]}", "school_id": sch_id, "student_id": sid,
                            "section_id": "", "attendance_date": date_str, "attendance_type": "daily",
                            "attendance_status": status, "excuse_code": excuse
                        })
                    else:
                        for sec_id in stu_to_sec.get(sid, []):
                            status = random.choices(["present", "absent", "tardy"], weights=[0.92, 0.04, 0.04])[0]
                            excuse = f"EXC-{random.randint(100,999)}" if status != "present" else ""
                            attendance_data.append({
                                "sis_id": f"att-{uuid.uuid4().hex[:10]}", "school_id": sch_id, "student_id": sid,
                                "section_id": sec_id, "attendance_date": date_str, "attendance_type": "section",
                                "attendance_status": status, "excuse_code": excuse
                            })

        # --- PHASE 3: SAVING ---
        progress.update(main_task, description=f"[yellow]Saving {dist_name}...[/yellow]")
        out_dir = os.path.join(base_output_dir, f"{dist_name}_Data")
        os.makedirs(out_dir, exist_ok=True)
        
        pd.DataFrame(schools_data).to_csv(f"{out_dir}/schools.csv", index=False)
        pd.DataFrame(teachers_data).to_csv(f"{out_dir}/teachers.csv", index=False)
        pd.DataFrame(staff_data).to_csv(f"{out_dir}/staff.csv", index=False)
        pd.DataFrame(students_data).drop_duplicates(subset=['Student_id']).to_csv(f"{out_dir}/students.csv", index=False)
        pd.DataFrame(sections_data).to_csv(f"{out_dir}/sections.csv", index=False)
        pd.DataFrame(enrollments_data).to_csv(f"{out_dir}/enrollments.csv", index=False)
        
        if resources_data: pd.DataFrame(resources_data).to_csv(f"{out_dir}/resources.csv", index=False)
        if attendance_data: pd.DataFrame(attendance_data).to_csv(f"{out_dir}/attendance.csv", index=False)

        progress.advance(main_task)
        console.print(f":white_check_mark: [green]{dist_name} Complete[/green]")

console.print("\n[bold blue]Generation Complete![/bold blue]")