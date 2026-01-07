import os
import random
import uuid
import datetime
import pandas as pd
from faker import Faker
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.prompt import IntPrompt, Confirm, Prompt, FloatPrompt
from rich.table import Table

fake = Faker('en_US')
console = Console()

# ==========================================
# 1. CONSTANTS & MAPPINGS
# ==========================================

GENERIC_DISTRICT_NAMES = [
    "MapleValley", "OakRiver", "SummitHeights", "PineCreek", 
    "LibertyUnion", "Heritage", "PioneerValley", "GrandView", 
    "Clearwater", "HopeSprings", "NorthStar", "GoldenPlains",
    "SilverLake", "WillowCreek", "Unity", "CedarRidge"
]
random.shuffle(GENERIC_DISTRICT_NAMES)

STATE_MAPPINGS = {
    "C4a": ("California", "CA"),
    "T3x": ("Texas", "TX"),
    "N3y": ("New York", "NY"),
    "F1a": ("Florida", "FL"),
    "W2a": ("Washington", "WA"),
    "I1l": ("Illinois", "IL"),
    "C0l": ("Colorado", "CO"),
    "A7z": ("Arizona", "AZ"),
    "G4a": ("Georgia", "GA"),
    "M4a": ("Massachusetts", "MA")
}
STATE_KEYS = list(STATE_MAPPINGS.keys())

# --- NEW: VALID CITY/ZIP MAPPING ---
# Format: "StateAbbr": [("City", "ZipPrefix")]
REAL_LOCATIONS = {
    "CA": [("San Francisco", "941"), ("Los Angeles", "900"), ("San Diego", "921"), ("Sacramento", "958"), ("Fresno", "937")],
    "TX": [("Austin", "733"), ("Houston", "770"), ("Dallas", "752"), ("San Antonio", "782"), ("Fort Worth", "761")],
    "NY": [("New York", "100"), ("Buffalo", "142"), ("Albany", "122"), ("Rochester", "146"), ("Syracuse", "132")],
    "FL": [("Miami", "331"), ("Orlando", "328"), ("Tampa", "336"), ("Jacksonville", "320"), ("Tallahassee", "323")],
    "WA": [("Seattle", "981"), ("Spokane", "992"), ("Tacoma", "984"), ("Vancouver", "986"), ("Bellevue", "980")],
    "IL": [("Chicago", "606"), ("Springfield", "627"), ("Peoria", "616"), ("Naperville", "605"), ("Rockford", "611")],
    "CO": [("Denver", "802"), ("Colorado Springs", "809"), ("Boulder", "803"), ("Aurora", "800"), ("Fort Collins", "805")],
    "AZ": [("Phoenix", "850"), ("Tucson", "857"), ("Mesa", "852"), ("Scottsdale", "852"), ("Chandler", "852")],
    "GA": [("Atlanta", "303"), ("Savannah", "314"), ("Augusta", "309"), ("Athens", "306"), ("Macon", "312")],
    "MA": [("Boston", "021"), ("Worcester", "016"), ("Springfield", "011"), ("Cambridge", "021"), ("Lowell", "018")]
}

# --- CLEVER COMPLIANT VALUES ---
CLEVER_RACE_VALUES = ["White", "Black or African American", "Asian", "American Indian or Alaska Native", "Native Hawaiian or Other Pacific Islander", "Two or more races", "Unknown"]
RACE_WEIGHTS = [0.50, 0.15, 0.06, 0.02, 0.01, 0.06, 0.20]

# ISO 639-3 (Updated to 'zho' but keeping 'chi' logic optional if needed)
LANGUAGE_MAP = { "eng": 0.70, "spa": 0.20, "vie": 0.03, "chi": 0.02, "ara": 0.02, "tgl": 0.01, "rus": 0.01, "som": 0.01 }
LANG_KEYS = list(LANGUAGE_MAP.keys())
LANG_WEIGHTS = list(LANGUAGE_MAP.values())

DISABILITY_MAP = { "AUT": "Autism", "DB": "Deaf-blindness", "DD": "Developmental delay", "EMN": "Emotional disturbance", "HI": "Hearing impairment", "ID": "Intellectual Disability", "MD": "Multiple disabilities", "OI": "Orthopedic impairment", "OHI": "Other health impairment", "SLD": "Specific learning disability", "SLI": "Speech or language impairment", "TBI": "Traumatic brain injury", "VI": "Visual impairment" }
DISABILITY_CODES = list(DISABILITY_MAP.keys())

# ==========================================
# 2. USER INPUT
# ==========================================
console.rule("[bold green]Clever Data Generator (v2.2 - Location Fix)[/bold green]")

ID_MODE = Prompt.ask("Select ID Mode", choices=["sequential", "alphanumeric"], default="alphanumeric")
NUM_DISTRICTS = IntPrompt.ask("Districts", default=1)
SCHOOLS_PER_DISTRICT = IntPrompt.ask("Schools per District", default=5)
TEACHERS_PER_SCHOOL = IntPrompt.ask("Teachers per School", default=10)
SECTIONS_PER_SCHOOL = IntPrompt.ask("Sections per School", default=4)
STUDENTS_PER_SECTION = IntPrompt.ask("Students per Section", default=20)

console.print("\n[bold yellow]-- Demographics --[/bold yellow]")
PROB_FRL = FloatPrompt.ask("Prob. Free/Reduced Lunch", default=0.45)
PROB_IEP = FloatPrompt.ask("Prob. IEP", default=0.12)
PROB_ELL = FloatPrompt.ask("Prob. ELL", default=0.10)
PROB_504 = FloatPrompt.ask("Prob. 504", default=0.05)
PROB_GIFTED = FloatPrompt.ask("Prob. Gifted", default=0.08)
PROB_DISABILITY = FloatPrompt.ask("Prob. Disability", default=0.11) 

if not Confirm.ask("Ready to generate?", default=True): exit()

# ==========================================
# 3. HELPER FUNCTIONS
# ==========================================
def get_hex_id(length=6): return uuid.uuid4().hex[:length]
def get_sequential_id(base, counter): return str(base + counter)

def generate_dob(grade):
    current_year = datetime.date.today().year
    grade_map = {'PK':4,'KG':5,'1':6,'2':7,'3':8,'4':9,'5':10,'6':11,'7':12,'8':13,'9':14,'10':15,'11':16,'12':17}
    target_age = grade_map.get(grade, 10)
    birth_year = current_year - target_age
    return fake.date_between(start_date=datetime.date(birth_year,1,1), end_date=datetime.date(birth_year,12,31)).strftime('%Y-%m-%d')

# ==========================================
# 4. GENERATION LOOP
# ==========================================
base_output_dir = 'clever_district_data'

with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn(), console=console) as progress:
    main_task = progress.add_task("[green]Generating...", total=NUM_DISTRICTS)

    for i in range(NUM_DISTRICTS):
        # District Setup
        dist_name = GENERIC_DISTRICT_NAMES[i % len(GENERIC_DISTRICT_NAMES)]
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

            # --- NEW LOCATION LOGIC ---
            # 1. Look up valid cities for this state
            valid_locations = REAL_LOCATIONS.get(state_abbr, [("City", "000")])
            # 2. Pick one random City/Zip pair
            city_name, zip_prefix = random.choice(valid_locations)
            # 3. Generate full 5-digit zip based on prefix
            full_zip = f"{zip_prefix}{random.randint(10, 99)}"

            schools_data.append({
                "School_id": school_id,
                "School_name": f"{fake.last_name()} {school_type}",
                "School_number": school_code,
                "Low_grade": low,
                "High_grade": high,
                "Principal": fake.name(),
                "Principal_email": f"principal.{school_id}@{email_domain}",
                "School_address": fake.street_address(),
                "School_city": city_name,     # Fixed
                "School_state": state_abbr,   # Fixed
                "School_zip": full_zip,       # Fixed
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

            # D. ROSTERING
            grade_list = [str(g) if g > 0 else 'KG' for g in range(int(low) if low.isdigit() else 0, (int(high) if high.isdigit() else 12) + 1)]

            for sec_idx in range(SECTIONS_PER_SCHOOL):
                sec_id = get_hex_id(8) if ID_MODE == 'alphanumeric' else get_sequential_id(base_id_seq, 50000 + sec_idx)
                p_teach = random.choice(school_teacher_ids)
                s_teach = random.choice([t for t in school_teacher_ids if t != p_teach]) if sec_idx == 0 else None
                s_grade = random.choice(grade_list)
                s_subj = random.choice(['Math', 'Science', 'ELA', 'History'])

                sections_data.append({
                    "School_id": school_id, "Section_id": sec_id, "Teacher_id": p_teach, "Teacher_2_id": s_teach,
                    "Name": f"{s_grade} - {s_subj} ({sec_idx+1})", "Grade": s_grade, "Subject": s_subj
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

                    f, l = fake.first_name(), fake.last_name()
                    
                    # Demographics
                    race = random.choices(CLEVER_RACE_VALUES, weights=RACE_WEIGHTS)[0]
                    lang = random.choices(LANG_KEYS, weights=LANG_WEIGHTS)[0]
                    
                    has_disability = "Y" if random.random() < PROB_DISABILITY else "N"
                    dis_code, dis_type = ("", "")
                    if has_disability == "Y":
                        code = random.choice(DISABILITY_CODES)
                        dis_code, dis_type = code, DISABILITY_MAP[code]

                    students_data.append({
                        "School_id": school_id, "Student_id": stu_id, "Student_number": stu_num, "State_id": state_id,
                        "Last_name": l, "First_name": f, "Grade": s_grade, "Gender": random.choice(['M', 'F']),
                        "DOB": generate_dob(s_grade), "Email_address": f"{f[0]}{l}{random.randint(10,99)}@{email_domain}".lower(),
                        "Race": race, "Home_language": lang,
                        "IEP_status": "Y" if random.random() < PROB_IEP else "N",
                        "FRL_status": "Y" if random.random() < PROB_FRL else "N",
                        "ELL_status": "Y" if random.random() < PROB_ELL else "N",
                        "Section_504_status": "Y" if random.random() < PROB_504 else "N",
                        "Gifted_status": "Y" if random.random() < PROB_GIFTED else "N",
                        "Disability_status": has_disability, "Disability_type": dis_type, "Disability_code": dis_code
                    })
                    enrollments_data.append({"School_id": school_id, "Section_id": sec_id, "Student_id": stu_id})

        # E. ADMIN
        if schools_data:
            admin_id = get_hex_id(7) if ID_MODE == 'alphanumeric' else str(base_id_seq + 99999)
            staff_data.insert(0, { "School_id": schools_data[0]['School_id'], "Staff_id": admin_id, "Staff_email": f"admin@{email_domain}", "First_name": "System", "Last_name": "Admin", "Department": "Central", "Title": "Admin" })
        
        # F. SAVE
        out_dir = os.path.join(base_output_dir, f"{dist_name}_Data")
        os.makedirs(out_dir, exist_ok=True)
        for name, data in [('schools', schools_data), ('teachers', teachers_data), ('staff', staff_data), ('sections', sections_data), ('enrollments', enrollments_data)]:
            pd.DataFrame(data).to_csv(f"{out_dir}/{name}.csv", index=False)
        pd.DataFrame(students_data).drop_duplicates(subset=['Student_id']).to_csv(f"{out_dir}/students.csv", index=False)
        
        progress.advance(main_task)
        console.print(f":white_check_mark: [green]{dist_name} Generated[/green]")

console.print("\n[bold blue]Done![/bold blue]")