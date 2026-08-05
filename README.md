# Clever Demo District Generator

A Python tool for generating synthetic, **Clever Schema-compliant** school district data at any scale. Designed for Partner Implementation Engineers and integration developers who need realistic, privacy-safe datasets for testing rostering integrations, SSO flows, and application logic.

Runs as a **browser-based web app** (Streamlit) or a **terminal CLI** (Rich). Both interfaces share the same generation engine.

---

## Quick Start

```bash
git clone https://github.com/your-org/demo-district-generator.git
cd demo-district-generator
python3 -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Web app (recommended):**
```bash
streamlit run app.py
```

**CLI:**
```bash
python3 cli.py
```

---

## Key Capabilities

- **Scalable generation** — from a single 5-school district to 500+ schools with hundreds of thousands of students, with zero ID collisions guaranteed
- **Realistic data at scale** — Census Bureau-sourced name pools (276,000 unique name combinations) with uniform sampling, preventing name repetition even at large scale
- **Correlated demographics** — Hispanic/Latino identity, home language (Spanish), and ELL status are derived from a single slider using national NCES averages, keeping all three fields internally consistent
- **Course catalog** — 117 grade-aware courses across 9 subjects (Math, ELA, Science, History, Art, PE, and summer programs) embedded in sections via `Course_name`, `Course_number`, and `Course_description`
- **School type pyramid** — districts automatically follow a realistic 60% Elementary / 20% Middle / 15% High / 5% Academy distribution at any size
- **39 edge case scenarios** — individually toggleable, grouped into single-day static scenarios and 3-day SFTP rotation scenarios
- **Excel-safe IDs** — prefixed alphanumeric IDs (`stu-`, `tch-`, `sch-`, `sec-`, `stf-`) prevent scientific notation misinterpretation
- **Multi-schema output** — Standard Clever CSV schema and/or AnySchool schema in a single run
- **Optional attendance data** — section-based or daily attendance generation across a configurable date range

---

## Repository Structure

```
demo-district-generator/
├── generator_core.py       # Generation engine — all logic lives here
├── app.py                  # Streamlit web UI
├── cli.py                  # Rich terminal CLI
├── add_courses_to_sections.py  # Standalone script to enrich an existing sections.csv
├── requirements.txt
├── README.md
└── docs/
    ├── configuration.md    # All config options and defaults
    ├── output-schema.md    # Output file structure and field reference
    ├── edge-cases.md       # All 39 edge case scenarios
    └── data-realism.md     # Name engine, demographics, and school distribution logic
```

---

## Documentation

- [Configuration Reference](docs/configuration.md) — all settings, defaults, and what they control
- [Output Schema](docs/output-schema.md) — file structure, field definitions, and schema variants
- [Edge Cases](docs/edge-cases.md) — all 39 scenarios with descriptions and usage guidance
- [Data Realism](docs/data-realism.md) — how names, demographics, school types, and courses are generated
