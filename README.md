# Clever Demo District generator

A high-performance Python utility for generating synthetic school district data that is **Clever Schema Compliant**. 

This tool is designed for developers and integration engineers who need robust, realistic, and privacy-safe datasets for testing rostering integrations (SFTP/CSV), SIS imports, and application logic.

## 🚀 Features

* **Pure Python:** No API keys or cloud dependencies required. Runs locally and instantly.

* **Clever Compliant:** Generates CSVs (`schools`, `students`, `teachers`, `sections`, `enrollments`) that match standard rostering schemas, including ISO language codes and standard race categories.

* **Smart Logic:**
    * **Real Locations:** Maps schools to valid City/Zip combinations based on State (e.g., Austin TX zips vs. NY zips).
    * **Dynamic Terms:** Automatically calculates School Year start/end dates based on your testing window.
    * **Demographics:** Configurable distribution of IEP, ELL, FRL, and Disability statuses.
    * **Gender Alignment:** Ensures student First Names match their Gender marker.
* **Supplemental Data:** Optional generation of **Granular Attendance** (Section-level or Daily) and **Resources** (textbooks/apps).

## 🛠️ Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-org/demo-district-generator.git](https://github.com/your-org/demo-district-generator.git)
    cd demo-district-generator
    ```

2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## ⚡ Usage

Run the main script:

```bash
python faker_district.py
```

## The "Quick Start" Workflow

When you run the script, you will be asked:

"Apply default settings?"

**Yes (y)**: Immediately generates data using the configuration defined in the DEFAULTS dictionary at the top of the script. Perfect for rapid regression testing.

**No (n)**: Enters Interactive Mode, allowing you to customize:

* Number of Districts/Schools/Students.

* Probability of demographics (IEP, FRL, etc.).

* Whether to include Attendance or Resource files.


### Output Structure

Data is generated in the `district_data_output/` directory. Each district gets its own folder:

```text
district_data/
└── MapleValley_Data/
    ├── schools.csv
    ├── teachers.csv
    ├── students.csv
    ├── staff.csv
    ├── sections.csv
    ├── enrollments.csv
    ├── attendance.csv  (Optional)
    └── resources.csv   (Optional)
```

### Configuration

You can permanently adjust the "Quick Start" baseline by editing the `DEFAULTS` dictionary at the top of `faker_district.py`:
```python
DEFAULTS = {
    "ID_MODE": "alphanumeric",
    "NUM_DISTRICTS": 1,
    "SCHOOLS_PER_DISTRICT": 5,
    "TEACHERS_PER_SCHOOL": 10,
    "SECTIONS_PER_SCHOOL": 15,    # Increased slightly to show off term splitting
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
```

### Data Logic & Notes

#### Dynamic Term Logic:

* **Configuration**: You define the structure (Semesters/Trimesters/Quarters) and the SCHOOL_START_YEAR (e.g., 2025).

* **Smart Dates**: The script automatically generates realistic date ranges (e.g., Semesters align with Winter Break).

* **Load Balancing**: Sections are distributed evenly across terms for each teacher. If a teacher has multiple sections, they will be split between Fall, Spring, and (optionally) Summer to create a realistic schedule.

#### Attendance Modes:

* **Daily**: One record per student per day.

* **Section**: One record per student per section per day (High volume).


**Privacy**: All Personally Identifiable Information (PII) is synthetically generated using Faker. No real student data is ever used.