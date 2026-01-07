import os
import random
import datetime
import pandas as pd
from faker import Faker
from rich.console import Console
from rich.prompt import Confirm, Prompt, IntPrompt

fake = Faker('en_US')
console = Console()

BASE_DIR = 'clever_district_data'

# ==========================================
# 1. HELPER FUNCTIONS
# ==========================================

def get_districts():
    """Scans the output directory for valid district folders."""
    if not os.path.exists(BASE_DIR):
        return []
    return [d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))]

def generate_date_range(start_date, days):
    """Generates a list of weekdays (Mon-Fri) starting from start_date."""
    dates = []
    current = start_date
    while len(dates) < days:
        # 0=Monday, 4=Friday, 5=Saturday, 6=Sunday
        if current.weekday() < 5: 
            dates.append(current)
        current += datetime.timedelta(days=1)
    return dates

# ==========================================
# 2. MODULE: ATTENDANCE
# ==========================================
def generate_attendance(district_path):
    console.print(f"[cyan]Generating Granular Attendance for {district_path}...[/cyan]")
    
    # Load required files
    students_df = pd.read_csv(os.path.join(district_path, 'students.csv'))
    
    # Check for enrollments if we want section-level data
    enrollments_path = os.path.join(district_path, 'enrollments.csv')
    has_enrollments = os.path.exists(enrollments_path)
    enrollments_df = pd.read_csv(enrollments_path) if has_enrollments else pd.DataFrame()
    
    # Config
    start_str = Prompt.ask("Start Date (YYYY-MM-DD)", default="2025-04-01")
    duration_days = IntPrompt.ask("Number of School Days", default=5) # Default lowered since data volume is higher
    
    # Mode Selection
    att_mode = Prompt.ask(
        "Attendance Mode", 
        choices=["Daily", "Section", "Mixed"], 
        default="Section" if has_enrollments else "Daily"
    )
    
    start_date = datetime.datetime.strptime(start_str, "%Y-%m-%d").date()
    valid_dates = generate_date_range(start_date, duration_days)
    
    attendance_data = []
    
    # Pre-process enrollments for fast lookup: Student_id -> [Section_ids]
    student_sections = {}
    if att_mode in ["Section", "Mixed"] and has_enrollments:
        console.print("Indexing enrollments for section lookup...")
        for _, row in enrollments_df.iterrows():
            sid = row['Student_id']
            if sid not in student_sections: student_sections[sid] = []
            student_sections[sid].append(row['Section_id'])

    console.print(f"Generating records for {len(valid_dates)} days...")

    for day in valid_dates:
        date_str = day.strftime("%Y-%m-%d") # ISO 8601 YYYY-MM-DD
        
        for _, student in students_df.iterrows():
            stu_id = student['Student_id']
            school_id = student['School_id']
            
            # Determine types to generate for this student today
            types_to_gen = []
            if att_mode == "Mixed":
                types_to_gen = ["daily"] if random.random() > 0.5 else ["section"]
            else:
                types_to_gen = [att_mode.lower()]

            for a_type in types_to_gen:
                if a_type == "daily":
                    # Generate 1 record per day
                    status = random.choices(["present", "absent", "tardy"], weights=[0.90, 0.05, 0.05])[0]
                    excuse = f"EXC-{random.randint(100,999)}" if status != "present" else ""
                    
                    attendance_data.append({
                        "sis_id": f"att-{uuid.uuid4().hex[:10]}",
                        "school_id": school_id,
                        "student_id": stu_id,
                        "section_id": "", # Empty for Daily
                        "attendance_date": date_str,
                        "attendance_type": "daily",
                        "attendance_status": status,
                        "excuse_code": excuse
                    })
                    
                elif a_type == "section":
                    # Generate 1 record per section
                    my_sections = student_sections.get(stu_id, [])
                    if not my_sections: continue # Skip if no enrollments
                    
                    for sec_id in my_sections:
                        # Higher chance of being present per section
                        status = random.choices(["present", "absent", "tardy"], weights=[0.92, 0.04, 0.04])[0]
                        excuse = f"EXC-{random.randint(100,999)}" if status != "present" else ""
                        
                        attendance_data.append({
                            "sis_id": f"att-{uuid.uuid4().hex[:10]}",
                            "school_id": school_id,
                            "student_id": stu_id,
                            "section_id": sec_id,
                            "attendance_date": date_str,
                            "attendance_type": "section",
                            "attendance_status": status,
                            "excuse_code": excuse
                        })

    # Save
    out_path = os.path.join(district_path, 'attendance.csv')
    pd.DataFrame(attendance_data).to_csv(out_path, index=False)
    console.print(f"[green]Attendance Generated![/green] ({len(attendance_data)} records)")

# ==========================================
# 3. MODULE: RESOURCES
# ==========================================
def generate_resources(district_path):
    console.print(f"[cyan]Generating Resources for {district_path}...[/cyan]")
    
    resources_data = []
    
    # Generic "District Library" Content
    # Format: (Title, Target Roles)
    library_pool = [
        # Math
        ("District Math: Algebra I", "student,teacher"),
        ("District Math: Geometry", "student,teacher"),
        ("Math Intervention Tools", "teacher"), # Teachers only
        
        # Science
        ("Virtual Lab: Biology", "student,teacher"),
        ("Chemistry Safety Guides", "teacher"),
        ("Physics Simulations", "student,teacher"),
        
        # ELA / Literacy
        ("District Digital Library (Sora)", "student,teacher"),
        ("Grammar & Composition Reference", "student,teacher"),
        ("Reading Assessment Portal", "teacher"), # Teachers only
        
        # History / Social Studies
        ("World Atlas Interactive", "student,teacher"),
        ("Primary Sources Database", "student,teacher"),
        
        # Admin / Tools
        ("Attendance Dashboard", "teacher"),
        ("Gradebook Pro", "teacher"),
        ("Student Portal Home", "student"),
        ("IT Help Desk", "student,teacher")
    ]
    
    for title, roles in library_pool:
        # Create a resource_id hash based on the title to keep it consistent
        # e.g., "RES-DIS-MATH-01"
        prefix = title.split(':')[0][:3].upper().replace(" ", "")
        suffix = str(abs(hash(title)))[:4]
        resource_id = f"RES-{prefix}-{suffix}"
        
        resources_data.append({
            "resource_id": resource_id,
            "title": title,
            "roles": roles 
        })
            
    # Save
    out_path = os.path.join(district_path, 'resources.csv')
    pd.DataFrame(resources_data).to_csv(out_path, index=False)
    console.print(f"[green]Resources Generated![/green] ({len(resources_data)} global items created)")

# ==========================================
# 4. MODULE: EXTENSIONS (Custom Fields)
# ==========================================
def generate_extensions(district_path):
    console.print(f"[cyan]Patching Students with Extension Fields...[/cyan]")
    
    file_path = os.path.join(district_path, 'students.csv')
    students_df = pd.read_csv(file_path)
    
    # Check if already patched to avoid duplicates
    if 'ext.locker_number' in students_df.columns:
        console.print("[yellow]Extensions already exist. Skipping.[/yellow]")
        return

    # Add Extension Columns
    # Note: Clever usually parses 'ext.' prefix or requires mapping. 
    # We will simulate data that requires mapping.
    
    students_df['ext.locker_number'] = [random.randint(100, 9999) for _ in range(len(students_df))]
    students_df['ext.bus_route'] = [random.choice(['Route A', 'Route B', 'Walk', 'Pickup']) for _ in range(len(students_df))]
    students_df['ext.dietary_restriction'] = [
        random.choice(['None', 'None', 'None', 'Peanut', 'Gluten', 'Vegan']) 
        for _ in range(len(students_df))
    ]

    # Overwrite the file
    students_df.to_csv(file_path, index=False)
    console.print("[green]Students.csv patched with ext fields![/green]")

# ==========================================
# 5. MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    console.rule("[bold magenta]Supplemental Data Generator[/bold magenta]")
    
    districts = get_districts()
    if not districts:
        console.print("[red]No district data found. Run the main generator first![/red]")
        exit()
        
    console.print(f"Found {len(districts)} districts: {', '.join(districts)}")
    
    # Selection
    target_dist = Prompt.ask("Enter District Name to process (or 'ALL')", choices=districts + ['ALL'], default=districts[0])
    
    targets = districts if target_dist == 'ALL' else [target_dist]
    
    # Feature Toggles
    do_attendance = Confirm.ask("Generate [cyan]Attendance[/cyan]?", default=True)
    do_resources = Confirm.ask("Generate [cyan]Resources[/cyan]?", default=False)
    do_extensions = Confirm.ask("Patch [cyan]Extension Fields[/cyan] (Lockers, Bus)?", default=False)

    for dist in targets:
        full_path = os.path.join(BASE_DIR, dist)
        console.rule(f"Processing {dist}")
        
        if do_attendance: generate_attendance(full_path)
        if do_resources: generate_resources(full_path)
        if do_extensions: generate_extensions(full_path)
        
    console.print("\n[bold magenta]All Tasks Complete![/bold magenta]")