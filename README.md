
# Clever Demo District Generator

A high-performance Python utility for generating synthetic, **Clever Schema Compliant** school district data.

This tool is designed for developers and integration engineers who need robust, realistic, and privacy-safe datasets for testing rostering integrations (SFTP/CSV), SIS imports, and application logic. It can be run either via a **Command Line Interface (CLI)** or a **Browser-Based Web App (Streamlit)**.

## 🚀 Key Features

-   **Monorepo Architecture:** A single source of truth for generation logic powers both a Web UI and a Terminal CLI.
    
-   **Memory-Efficient Streaming:** Uses a chunked file-streaming approach to write CSVs on the fly, allowing you to generate massive districts (100+ schools) without crashing your machine's RAM.
    
-   **Multi-Schema Support & Validation:**
    
    -   **Standard:** Standard rostering CSVs (`schools`, `students`, `teachers`, `sections`, `enrollments`).
        
    -   **AnySchool:** Generates `users.csv` and `sections.csv`, applying strict Clever-compliant validation mappings automatically (e.g., transforming `"KG"` to `"Kindergarten"` and `"ELA"` to `"english/language arts"`).
        
-   **Variance & Ranges:** Input ranges (e.g., "15-30 teachers") to create organic, non-uniform districts.
    
-   **Ratio-Based Scheduling:** Define workload by "Sections per Teacher" to ensure realistic data shapes regardless of district size.
    
-   **"Two-Pass" Summer School:** Summer sessions are generated as an overlay (~35% of teachers), ensuring realistic coverage without disrupting core academic term logic.
    
-   **Privacy First:** All PII is synthetically generated using `Faker`. No real student data is ever used.
    

## 🏗️ Repository Structure

-   **`generator_core.py`**: The "Brain." Contains all the data generation logic, math, schema mappings, and file-streaming capabilities.
    
-   **`app.py`**: The "Web Face." A Streamlit interface that collects user inputs via the browser and passes them to the core.
    
-   **`cli.py`**: The "Terminal Face." A Rich-powered CLI that collects user inputs via the terminal and passes them to the core.
    

## 🛠️ Installation

1.  **Clone the repository:**
    
    Bash
    
    ```
    git clone https://github.com/your-org/demo-district-generator.git
    cd demo-district-generator
    
    ```
    
2.  **Create and activate a Virtual Environment:**
    
    Bash
    
    ```
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    
    ```
    
3.  **Install Dependencies:**
    
    Bash
    
    ```
    pip install -r requirements.txt
    
    ```
    
    _(Note: Your `requirements.txt` should include `streamlit`, `pandas`, `faker`, `rich`, and `altair<5`)_
    

## ⚡ Usage

You can generate data using whichever interface you prefer. Both utilize the exact same underlying logic and output the same files.

### Option 1: The Web App (Recommended)

Launch the browser-based dashboard. Perfect for visual configuration and downloading zipped outputs directly.

Bash

```
streamlit run app.py

```

### Option 2: The Command Line Interface

Run the pure terminal version. Perfect for quick local runs, SSH environments, or users who prefer the keyboard.

Bash

```
python cli.py

```

## 📂 Output Structure

Data is generated in the `district_data_output/` directory. Depending on your schema selection, the files will be organized into subfolders:

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

_(If using the Web App, this folder is automatically zipped and provided as a download button)._

## 🧠 Configuration & Logic Details

### Configuration Defaults

You can permanently adjust the baseline defaults for both tools by editing the `DEFAULTS` dictionary at the top of `generator_core.py`:

Python

```
DEFAULTS = {
    "NUM_DISTRICTS": 1,
    "SCHOOLS_PER_DISTRICT": 5,
    "TEACHERS_PER_SCHOOL": "15-30",      # Min-Max Range
    "STUDENTS_PER_SECTION": "18-32",     # Min-Max Range
    "SECTIONS_PER_TEACHER_TERM": 5,      # Workload Ratio
    "SCHOOL_START_YEAR": "2025",
    "NUM_TERMS": 2,
    "INCLUDE_SUMMER": True,
    # ...
}

```

### AnySchool Schema Mappings

To comply with strict Clever AnySchool validation, the script automatically transforms internal readable values to schema-compliant strings right before writing to disk:

-   **Grades:** `KG` $\rightarrow$ `Kindergarten`, `PK` $\rightarrow$ `PreKindergarten`
    
-   **Subjects:** `ELA` $\rightarrow$ `english/language arts`, `History` $\rightarrow$ `social studies`, `Art` $\rightarrow$ `arts and music`, etc.