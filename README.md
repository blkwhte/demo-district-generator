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
python generate_unified_district.py
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

Data is generated in the `district_data/` directory. Each district gets its own folder:

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

You can permanently adjust the "Quick Start" baseline by editing the `DEFAULTS` dictionary at the top of `generate_unified_district.py`:

```python
DEFAULTS = {
    "NUM_DISTRICTS": 1,
    "SCHOOLS_PER_DISTRICT": 5,
    "TEACHERS_PER_SCHOOL": 10,
    
    # Toggle extra datasets
    "DO_ATTENDANCE": False, 
    "DO_RESOURCES": False,

    # Adjust Demographic Probabilities (0.0 - 1.0)
    "PROB_FRL": 0.45,       # Free/Reduced Lunch
    "PROB_IEP": 0.12,       # Individualized Education Program
    # ...
}
```

### Data Logic & Notes

* **Term Dates:** The script calculates the term based on the `ATT_START_DATE`.
    * *Jan - July:* Maps to the **previous** Fall start (e.g., July 2025 = 2024-2025 School Year).
    * *Aug - Dec:* Maps to the **current** Fall start (e.g., Aug 2025 = 2025-2026 School Year).
* **Attendance Modes:**
    * **Daily:** One record per student per day.
    * **Section:** One record per student *per section* per day (High volume).
* **Privacy:** All Personally Identifiable Information (PII) is synthetically generated using `Faker`. No real student data is ever used.