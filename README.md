# Clever Demo District Generator (containerized)

A high-performance Python utility for generating synthetic school district data that is **Clever Schema Compliant**.

This tool is designed for developers and integration engineers who need robust, realistic, and privacy-safe datasets for testing rostering integrations (SFTP/CSV), SIS imports, and application logic.

## 🚀 Features

- **Web Interface (Streamlit):** No more CLI prompts. Configure and generate data via a clean, browser-based dashboard.
    
- **Docker Ready:** Fully containerized for easy deployment on AWS, Azure, or local machines without environment conflicts.
    
- **Multi-Schema Support:**
    
    - **Standard:** Standard rostering CSVs (`schools`, `students`, `teachers`, `sections`, `enrollments`).
        
    - **AnySchool:** Supports the flat-file `users.csv` and `sections.csv` schema.
        
- **Smart Logic:**
    
    - **Variance & Ranges:** Input ranges (e.g., "15-30 teachers") to create organic, non-uniform districts.
        
    - **Ratio-Based Scheduling:** Define workload by "Sections per Teacher" rather than arbitrary totals.
        
    - **"Two-Pass" Summer School:** Summer sessions are generated as an overlay, ensuring realistic coverage (~35% of teachers) without messing up core term logic.
        
- **Privacy First:** All PII is synthetically generated using `Faker`. No real student data is ever used.
    

## 🛠️ Installation

### Option A: Local Python (Streamlit)

1. **Clone the repository:**
    
    Bash
    
    ```
    git clone https://github.com/your-org/demo-district-generator.git
    cd demo-district-generator
    ```
    
2. **Create a Virtual Environment:**
    
    Bash
    
    ```
    python3 -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    ```
    
3. **Install Dependencies:**
    
    Bash
    
    ```
    pip install -r requirements.txt
    ```
    
4. **Run the App:**
    
    Bash
    
    ```
    streamlit run faker_district.py
    ```
    
    _This will open the generator in your default web browser._
    

---

### Option B: Docker (Containerized)

Ideal for keeping your local machine clean or hosting on a shared server (AWS EC2/DigitalOcean).

1. **Build the Image:**
    
    Bash
    
    ```
    docker build -t district-gen .
    ```
    
2. **Run the Container:**
    
    Bash
    
    ```
    docker run -p 8501:8501 district-gen
    ```
    
3. **Access the App:**
    
    Open your browser and navigate to `http://localhost:8501`.
    

## ⚙️ Configuration & Usage

The Web UI is split into two sections: **Sidebar** (High-level config) and **Main Form** (Deep logic).

### 1. Structure & Format (Sidebar)

- **ID Mode:** `Alphanumeric` (GUIDs) or `Sequential` (Integer-based, easier to read).
    
- **Output Schema:** Choose `Standard`, `AnySchool`, or `Both`.
    
- **File Format:** CSV or JSON.
    

### 2. Ranges & Ratios (Main Form)

Instead of static numbers, this tool uses ranges to create variance between schools.

- **Teachers per School:** Accepts a range (e.g., `15-30`). The script picks a random number within this range for _each_ school generated.
    
- **Students per Section:** Accepts a range (e.g., `18-32`). Used to calculate enrollment density.
    
- **Sections per Teacher (Term):** The "Workload Ratio." If set to **5**, every teacher will teach 5 classes per term.
    

### 3. Term Logic

- **Core Terms:** Choose 2 (Semesters), 3 (Trimesters), or 4 (Quarters).
    
- **Summer Session:** If checked, the script runs a "Second Pass" to enroll ~30% of the student body in summer courses.
    

### 4. Advanced Settings

- **Email Domains:** Force a specific domain (e.g., `@test-district.org`) or let the script auto-generate based on the District Name.
    
- **Username Format:** Options for `first.last`, `f_last`, etc.
    
- **Supplemental Data:** Toggles for Contacts, Extensions, Resources, and Attendance.
    

## 📂 Output Structure

When you click **"Download Data (ZIP)"**, the archive will contain the following structure (depending on your Schema selection):

Plaintext

```
district_data_output/
└── MapleValley_Data/
    ├── standard/
    │   ├── schools.csv
    │   ├── teachers.csv
    │   ├── students.csv
    │   ├── staff.csv
    │   ├── sections.csv
    │   └── enrollments.csv
    └── anyschool/
        ├── users.csv
        └── sections.csv
```

## 🧠 Data Logic & Notes

### Ratio-Based Generation

Unlike previous versions where you defined a "Total Sections" count, V9 uses a **Ratio System**:

1. **Core Year:** The script iterates through every teacher.
    
2. **Assignment:** It assigns `N` sections (defined by you) for _every_ core term.
    
    - _Example:_ 2 Terms, 5 Sections/Teacher = 10 Sections total per teacher.
        
3. **Enrollment:** It calculates the required student count to fill those sections based on your `Students per Section` range.
    

### Summer School Overlay

Summer school is no longer part of the core rotation. It is generated via an **Overlay Method**:

- **Teachers:** A random sample (~35%) of teachers are assigned 1-2 extra sections labeled "Summer".
    
- **Students:** A random sample (~30%) of students are enrolled in these sections.
    
- **Result:** You get realistic summer data without needing to manually calculate "extra" sections in your configuration.
    

### AnySchool Schema

If enabled, the script performs a post-processing transformation:

- **Flattens** `teachers`, `staff`, and `students` into a single `users.csv`.
    
- **Converts** dates to `MM/DD/YYYY` format.
    
- **Joins** enrollment data directly into `sections.csv`.
    

### Default Configuration (`DEFAULTS`)

You can adjust the baseline settings by editing the `DEFAULTS` dictionary in `faker_district.py`:

```
DEFAULTS = {
    # Structure
    "NUM_DISTRICTS": 1,
    "SCHOOLS_PER_DISTRICT": 5,
    
    # Ranges & Ratios
    "TEACHERS_PER_SCHOOL": "15-30",      # Min-Max Range
    "STUDENTS_PER_SECTION": "18-32",     # Min-Max Range
    "SECTIONS_PER_TEACHER_TERM": 5,      # Workload Ratio
    
    # Term Configuration
    "SCHOOL_START_YEAR": "2025",
    "NUM_TERMS": 2,
    "INCLUDE_SUMMER": True,
    
    # ... Demographics and Toggles ...
}
```