import os
import random
import uuid
import datetime
import pandas as pd
from faker import Faker
from pydantic import BaseModel, EmailStr
from typing import Literal, List, Optional

# Import Rich for UI
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.prompt import IntPrompt, Confirm, Prompt
from rich.table import Table

# Initialize Faker and Console
fake = Faker('en_US')
console = Console()

# ==========================================
# 1. CONFIGURATION & CONSTANTS
# ==========================================

# Generic District Names (Same as before)
GENERIC_DISTRICT_NAMES = [
    "MapleValley", "OakRiver", "SummitHeights", "PineCreek", 
    "LibertyUnion", "Heritage", "PioneerValley", "GrandView", 
    "Clearwater", "HopeSprings", "NorthStar", "GoldenPlains",
    "SilverLake", "WillowCreek", "Unity", "CedarRidge"
]
random.shuffle(GENERIC_DISTRICT_NAMES)

# State Mappings
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

# ==========================================
# 2. USER INPUT
# ==========================================

console.rule("[bold green]School Data Generator (Pure Python)[/bold green]")

ID_MODE = Prompt.ask("Select ID Mode", choices=["sequential", "alphanumeric"], default="alphanumeric")
NUM_DISTRICTS = IntPrompt.ask("How many [cyan]Districts[/cyan]?", default=1)
SCHOOLS_PER_DISTRICT = IntPrompt.ask("How many [cyan]Schools per District[/cyan]?", default=5)
TEACHERS_PER_SCHOOL = IntPrompt.ask("How many [cyan]Teachers per School[/cyan]?", default=10)
SECTIONS_PER_SCHOOL = IntPrompt.ask("How many [cyan]Sections per School[/cyan]?", default=4)
STUDENTS_PER_SECTION = IntPrompt.ask("How many [cyan]Students per Section[/cyan]?", default=20)
INCLUDE_CO_TEACHERS = Confirm.ask("Include [cyan]Co-Teachers[/cyan]?", default=True)

# Display Summary
summary_table = Table(title="Configuration Summary")
summary_table.add_column("Setting", style="cyan")
summary_table.add_column("Value", style="magenta")
summary_table.add_row("Engine", "Pure Python (Faker)")
summary_table.add_row("ID Mode", ID_MODE.upper())
summary_table.add_row("Districts", str(NUM_DISTRICTS))
summary_table.add_row("Schools/District", str(SCHOOLS_PER_DISTRICT))
summary_table.add_row("Est. Students", str(NUM_DISTRICTS * SCHOOLS_PER_DISTRICT * SECTIONS_PER_SCHOOL * STUDENTS_PER_SECTION))

console.print(summary_table)
if not Confirm.ask("Ready to generate?", default=True):
    exit()

# ==========================================
# 3. HELPER FUNCTIONS (The Logic Engine)
# ==========================================

def get_hex_id(length=6):
    """Generates a random hex string of fixed length."""
    return uuid.uuid4().hex[:length]

def get_sequential_id(base, counter):
    """Returns a simple integer ID string."""
    return str(base + counter)

def generate_dob(grade):
    """Generates a realistic DOB based on grade level."""
    # Rough mapping: K=5yo, 12=17/18yo
    current_year = datetime.date.today().year
    
    grade_map = {
        'PK': 4, 'KG': 5, '1': 6, '2': 7, '3': 8, '4': 9, '5': 10,
        '6': 11, '7': 12, '8': 13, '9': 14, '10': 15, '11': 16, '12': 17
    }
    target_age = grade_map.get(grade, 10)
    birth_year = current_year - target_age
    
    start_date = datetime.date(birth_year, 1, 1)
    end_date = datetime.date(birth_year, 12, 31)
    return fake.date_between(start_date=start_date, end_date=end_date).strftime('%Y-%m-%d')

# ==========================================
# 4. DATA GENERATION LOOPS
# ==========================================

base_output_dir = 'school_district_data'

with Progress(
    SpinnerColumn(), TextColumn("[progress.description]{task.description}"), 
    BarColumn(), console=console
) as progress:

    total_ops = NUM_DISTRICTS
    main_task = progress.add_task("[green]Generating Districts...", total=total_ops)

    for i in range(NUM_DISTRICTS):
        # --- DISTRICT SETUP ---
        dist_name = GENERIC_DISTRICT_NAMES[i % len(GENERIC_DISTRICT_NAMES)]
        state_key = STATE_KEYS[i % len(STATE_KEYS)]
        state_name, state_abbr = STATE_MAPPINGS[state_key]
        email_domain = f"{dist_name.lower()}.k12.edu"
        
        # ID Prefixes
        district_prefix = str(10 + i) # 10, 11, 12...
        base_id_seq = (i + 1) * 100000 

        # Containers
        schools_data = []
        teachers_data = []
        staff_data = []
        students_data = []
        sections_data = []
        enrollments_data = []

        # --- A. GENERATE SCHOOLS ---
        for s_idx in range(SCHOOLS_PER_DISTRICT):
            # School ID Logic
            if ID_MODE == 'alphanumeric':
                # Length 5-6
                s_len = random.choice([5, 6])
                school_id = get_hex_id(s_len)
            else:
                school_id = get_sequential_id(base_id_seq, s_idx * 100)

            # School Info
            school_type = random.choice(['Elementary', 'Middle', 'High', 'Academy', 'Charter'])
            s_name = f"{fake.last_name()} {school_type}"
            school_code_2digit = f"{s_idx + 1:02d}" # 01, 02...
            
            # Grade Config
            if 'Elementary' in school_type: low, high = 'KG', '5'
            elif 'Middle' in school_type: low, high = '6', '8'
            elif 'High' in school_type: low, high = '9', '12'
            else: low, high = 'KG', '12'

            schools_data.append({
                "School_id": school_id,
                "School_name": s_name,
                "School_number": school_code_2digit,
                "Low_grade": low,
                "High_grade": high,
                "Principal": fake.name(),
                "Principal_email": f"principal.{school_id}@{email_domain}",
                "School_address": fake.street_address(),
                "School_city": fake.city(),
                "School_state": state_abbr,
                "School_zip": fake.zipcode_in_state(state_abbr),
                "School_phone": fake.phone_number()
            })

            # --- B. GENERATE TEACHERS ---
            school_teacher_ids = []
            for t_idx in range(TEACHERS_PER_SCHOOL):
                # Teacher ID Logic
                if ID_MODE == 'alphanumeric':
                    teacher_id = get_hex_id(7) # Fixed 7 chars
                    teacher_num = f"T-{random.randint(100000, 999999)}"
                    state_t_id = f"{state_abbr}-{teacher_num}"
                else:
                    teacher_id = get_sequential_id(base_id_seq, (s_idx * 1000) + t_idx)
                    teacher_num = teacher_id
                    state_t_id = teacher_id

                first, last = fake.first_name(), fake.last_name()
                
                teachers_data.append({
                    "School_id": school_id,
                    "Teacher_id": teacher_id,
                    "Teacher_number": teacher_num,
                    "State_teacher_id": state_t_id,
                    "Teacher_email": f"{first[0].lower()}{last.lower()}@{email_domain}",
                    "First_name": first,
                    "Last_name": last,
                    "Title": "Teacher"
                })
                school_teacher_ids.append(teacher_id)

            # --- C. GENERATE STAFF (2 Per School) ---
            for st_idx in range(2):
                if ID_MODE == 'alphanumeric':
                    staff_id = get_hex_id(7)
                else:
                    staff_id = get_sequential_id(base_id_seq, 9000 + (s_idx * 10) + st_idx)
                
                staff_first, staff_last = fake.first_name(), fake.last_name()
                
                staff_data.append({
                    "School_id": school_id,
                    "Staff_id": staff_id,
                    "Staff_email": f"{staff_first}.{staff_last}@{email_domain}",
                    "First_name": staff_first,
                    "Last_name": staff_last,
                    "Department": "Administration",
                    "Title": "Staff"
                })

            # --- D. ROSTERING (Sections & Students) ---
            # Grades to roster based on school type
            available_grades = []
            if low == 'KG': start_g = 0
            elif low == 'PK': start_g = -1
            elif low == 'K': start_g = 0
            else: start_g = int(low)
            
            end_g = int(high) if high.isdigit() else 12
            grade_list = [str(g) if g > 0 else 'KG' for g in range(start_g, end_g + 1)]

            for sec_idx in range(SECTIONS_PER_SCHOOL):
                # Section ID
                if ID_MODE == 'alphanumeric':
                    section_id = get_hex_id(8)
                else:
                    section_id = get_sequential_id(base_id_seq, 50000 + (s_idx * 100) + sec_idx)

                # Assign Teacher
                primary_teacher = random.choice(school_teacher_ids)
                secondary_teacher = None
                if INCLUDE_CO_TEACHERS and sec_idx == 0: # First section gets co-teacher
                    options = [t for t in school_teacher_ids if t != primary_teacher]
                    if options: secondary_teacher = random.choice(options)
                
                section_grade = random.choice(grade_list)
                section_subject = random.choice(['Math', 'Science', 'English', 'History', 'Art'])

                sections_data.append({
                    "School_id": school_id,
                    "Section_id": section_id,
                    "Teacher_id": primary_teacher,
                    "Teacher_2_id": secondary_teacher,
                    "Name": f"{section_grade} - {section_subject} ({sec_idx+1})",
                    "Grade": section_grade,
                    "Subject": section_subject
                })

                # Enroll Students
                for stu_idx in range(STUDENTS_PER_SECTION):
                    # Student ID Logic
                    if ID_MODE == 'alphanumeric':
                        # Length 6
                        student_id = get_hex_id(6)
                        # Number: District Prefix + Random
                        random_suffix = random.randint(100000, 999999)
                        student_number = f"{district_prefix}{random_suffix}"
                        # State ID: State - SchoolCode - StudentNum
                        state_student_id = f"{state_abbr}-{school_code_2digit}-{student_number}"
                    else:
                        student_id = get_sequential_id(base_id_seq, 200000 + (s_idx * 1000) + (sec_idx * 100) + stu_idx)
                        student_number = student_id
                        state_student_id = student_id

                    s_first, s_last = fake.first_name(), fake.last_name()
                    
                    # Create Student Record
                    # Note: In a real DB, we'd check if student exists. 
                    # Here, we generate fresh students for simplicity per section 
                    # (or you can cache them to reuse across sections)
                    
                    student_obj = {
                        "School_id": school_id,
                        "Student_id": student_id,
                        "Student_number": student_number,
                        "State_id": state_student_id,
                        "Last_name": s_last,
                        "First_name": s_first,
                        "Grade": section_grade,
                        "Gender": random.choice(['M', 'F']),
                        "DOB": generate_dob(section_grade),
                        "Student_email": f"{s_first[0]}{s_last}{random.randint(10,99)}@{email_domain}".lower()
                    }
                    students_data.append(student_obj)

                    # Create Enrollment
                    enrollments_data.append({
                        "School_id": school_id,
                        "Section_id": section_id,
                        "Student_id": student_id
                    })

        # --- E. SPECIAL ROLES (Admin & Dual) ---
        # 1. District Admin
        if schools_data:
            admin_school_id = schools_data[0]['School_id']
            admin_id = get_hex_id(7) if ID_MODE == 'alphanumeric' else str(base_id_seq + 99999)
            staff_data.insert(0, {
                "School_id": admin_school_id,
                "Staff_id": admin_id,
                "Staff_email": f"admin@{email_domain}",
                "First_name": "System",
                "Last_name": "Administrator",
                "Department": "Central Office",
                "Title": "District Administrator"
            })
            
        # 2. Dual Role
        if teachers_data:
            target = teachers_data[0]
            dual_id = (target['Teacher_id'] + "D")[:7] if ID_MODE == 'alphanumeric' else str(base_id_seq + 99998)
            staff_data.append({
                "School_id": target['School_id'],
                "Staff_id": dual_id,
                "Staff_email": target['Teacher_email'], # MATCHING EMAIL
                "First_name": target['First_name'],
                "Last_name": target['Last_name'],
                "Department": "Dual Role Test",
                "Title": "Teacher & Support Staff"
            })

        # --- F. SAVE TO CSV ---
        out_dir = os.path.join(base_output_dir, f"{dist_name}_Data")
        os.makedirs(out_dir, exist_ok=True)
        
        pd.DataFrame(schools_data).to_csv(f"{out_dir}/schools.csv", index=False)
        pd.DataFrame(teachers_data).to_csv(f"{out_dir}/teachers.csv", index=False)
        pd.DataFrame(staff_data).to_csv(f"{out_dir}/staff.csv", index=False)
        # Deduplicate students (since we generated per section)
        df_students = pd.DataFrame(students_data).drop_duplicates(subset=['Student_id'])
        df_students.to_csv(f"{out_dir}/students.csv", index=False)
        
        pd.DataFrame(sections_data).to_csv(f"{out_dir}/sections.csv", index=False)
        pd.DataFrame(enrollments_data).to_csv(f"{out_dir}/enrollments.csv", index=False)

        progress.advance(main_task)
        console.print(f":white_check_mark: [green]{dist_name} Generated[/green] ({len(df_students)} Students)")

console.print("\n[bold blue]All Districts Complete![/bold blue]")