
# Clever Demo District Generator (CLI Version)

A high-performance Python CLI utility for generating synthetic school district data that is **Clever Schema Compliant**.

This tool is designed for developers and integration engineers who need robust, realistic, and privacy-safe datasets for testing rostering integrations (SFTP/CSV), SIS imports, and application logic.

## 🚀 Features

- **Pure Python CLI:** Runs locally in your terminal with a rich, interactive user interface.
    
- **Multi-Schema Support:**
    
    - **Standard:** Generates standard rostering CSVs (`schools`, `students`, `teachers`, `sections`, `enrollments`).
        
    - **AnySchool:** Supports the flat-file `users.csv` and `sections.csv` schema.
        
- **Variance & Ranges:** Supports "Min-Max" ranges (e.g., `15-30`) for teachers and students, creating organic, non-uniform school sizes.
    
- **Ratio-Based Scheduling:** Logic generates sections based on **Workload Ratios** (e.g., "5 classes per teacher") rather than arbitrary totals, ensuring realistic data shapes regardless of district size.
    
- **"Two-Pass" Summer School:** Summer sessions are generated as an overlay (~35% of teachers), ensuring realistic coverage without disrupting core academic term logic.
    
- **Privacy First:** All PII is synthetically generated using `Faker`. No real student data is ever used.
    

## 🛠️ Installation

1. **Clone the repository:**
    
    Bash
    
    ```
    git clone https://github.com/your-org/demo-district-generator.git
    cd demo-district-generator
    ```
    
2. **Create a Virtual Environment (Recommended):**
    
    Bash
    
    ```
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
    
3. **Install Dependencies:**
    
    Bash
    
    ```
    pip install pandas faker rich
    ```
    

## ⚡ Usage

Run the main script:

Bash

```
python faker_district.py
```

### The Workflow

When you run the script, you will be asked:

> **"Apply ALL default settings?"**

1. **Yes (y):** Immediately generates data using the configuration defined in the `DEFAULTS` dictionary. Perfect for rapid regression testing.
    
2. **No (n):** Enters **Interactive Mode**, allowing you to customize:
    
    - **Structure:** Number of Districts, Schools.
        
    - **Ranges:** Teachers per school (e.g., "20-40") and Students per section.
        
    - **Ratios:** How many sections a single teacher leads per term.
        
    - **Schema:** Output `Standard`, `AnySchool`, or `Both`.
        
    - **Terms:** Academic start year and Term structure (Semesters/Trimesters/Quarters).
        
    - **Demographics:** Probability of IEP, FRL, ELL, etc.
        

## 📂 Output Structure

Data is generated in the `district_data_output/` directory. Depending on your **Schema** selection, the files will be organized into subfolders:

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

### 1. Ratio & Range Logic

Unlike older generators that required you to calculate "Total Sections," this tool uses a **Workload Ratio**:

- **Teachers:** You define a range (e.g., `15-30`). The script picks a random count for each school.
    
- **Sections:** You define the `SECTIONS_PER_TEACHER_TERM` (Default: 5).
    
    - _Math:_ If a school has 20 teachers and 2 terms, the script generates `20 * 2 * 5 = 200` sections.
        
- **Enrollment:** The script calculates the students needed to fill those sections based on your `STUDENTS_PER_SECTION` range (e.g., `18-32`).
    

### 2. Dynamic Term Logic

- **Core Terms:** You define the structure (Semesters/Trimesters/Quarters). The script maps realistic dates (e.g., Semesters align with Winter Break).
    
- **Summer Overlay:** Summer is no longer treated as a "3rd Semester." It is generated via a **Second Pass**:
    
    - **Teachers:** A random sample (~35%) are assigned extra "Summer" sections.
        
    - **Students:** A random sample (~30%) are enrolled in these sections.
        

### 3. AnySchool Transformation

If `AnySchool` or `Both` is selected, the script performs an in-memory transformation:

- Flattens `teachers`, `staff`, and `students` into a single `users.csv`.
    
- Converts standard `YYYY-MM-DD` dates to `MM/DD/YYYY`.
    
- Joins enrollment data directly into `sections.csv`.
    

### 4. Configuration

You can permanently adjust the "Quick Start" baseline by editing the `DEFAULTS` dictionary at the top of `faker_district.py`:

Python

```
DEFAULTS = {
    # Ranges (Strings allow "min-max")
    "TEACHERS_PER_SCHOOL": "15-30",
    "STUDENTS_PER_SECTION": "18-32",
    
    # Workload Ratio
    "SECTIONS_PER_TEACHER_TERM": 5, 

    # Term Configuration
    "SCHOOL_START_YEAR": "2025",
    "NUM_TERMS": 2, 
    "INCLUDE_SUMMER": True,
    
    # Output Control
    "OUTPUT_SCHEMA": "standard", # standard, anyschool, or both
    
    # ...
}
```