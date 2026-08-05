# Configuration Reference

All settings are available in both the web app (sidebar + expanders) and the CLI (interactive prompts). Defaults can also be permanently changed by editing the `DEFAULTS` dictionary in `generator_core.py`.

---

## District Structure

| Setting | Default | Description |
|---|---|---|
| `NUM_DISTRICTS` | `1` | Number of districts to generate. Each district gets its own output folder. |
| `SCHOOLS_PER_DISTRICT` | `5` | Number of schools per district. School types are distributed automatically — see [Data Realism](data-realism.md). |
| `TEACHERS_PER_SCHOOL` | `"15-30"` | Range string. A random value within the range is picked per school, creating organic variance. |
| `STUDENTS_PER_SECTION` | `"18-32"` | Range string. Controls how many students are enrolled into each section. |
| `SECTIONS_PER_TEACHER_TERM` | `5` | How many sections each teacher is assigned per academic term. |

## Academic Calendar

| Setting | Default | Description |
|---|---|---|
| `SCHOOL_START_YEAR` | `"2025"` | The fall start year. A 2025 value generates terms spanning 2025–2026. |
| `NUM_TERMS` | `2` | Number of academic terms per year (2 = semesters, 3 = trimesters, 4 = quarters). |
| `INCLUDE_SUMMER` | `True` | Whether to generate a summer session overlay for ~35% of teachers. |

## Output

| Setting | Default | Description |
|---|---|---|
| `ID_MODE` | `"alphanumeric"` | `"alphanumeric"` generates prefixed hex IDs (e.g. `stu-a3f9b2`). `"sequential"` generates numeric IDs. |
| `OUTPUT_SCHEMA` | `"standard"` | `"standard"` for Clever CSV schema, `"anyschool"` for AnySchool schema, `"both"` for both. |
| `EMAIL_DOMAIN` | `""` | Custom email domain. Leave blank to auto-generate `{districtname}.k12.edu`. |
| `USERNAME_FMT` | `"first.last"` | Username format. Options: `first.last`, `f.last`, `f_last`, `flast`. |

## Demographics

These control the probability that any given student has each attribute. All values are floats between 0.0 and 1.0.

| Setting | Default | Notes |
|---|---|---|
| `PROB_FRL` | `0.45` | Free/Reduced Lunch eligibility. |
| `PROB_IEP` | `0.12` | Individualized Education Program. |
| `PROB_HISPANIC` | `0.19` | Hispanic/Latino identity. **This is a cascade slider** — raising it also increases Spanish home language speakers and ELL students proportionally. See [Data Realism](data-realism.md) for details. |
| `PROB_504` | `0.05` | Section 504 Plan. |
| `PROB_GIFTED` | `0.08` | Gifted/talented designation. |
| `PROB_DISABILITY` | `0.11` | Disability status. Disability type is randomly drawn from a weighted set (Autism, SLD, SLI). |

> **Note:** `ELL_status` and `Home_language` are not standalone sliders — they are derived from `PROB_HISPANIC` using a correlation matrix. See [Data Realism](data-realism.md).

## Optional Features

| Setting | Default | Description |
|---|---|---|
| `DO_CONTACTS` | `True` | Whether to include household contact rows for each student (parent/guardian name, phone, email, relationship). |
| `DO_EXTENSIONS` | `False` | Whether to populate `ext.locker_number` and `ext.bus_route` extension fields on student rows. |
| `DO_ATTENDANCE` | `False` | Whether to generate an `attendance.csv` file. No file is created when `False`. |
| `ATT_START_DATE` | `"2025-09-01"` | Start date for attendance records (ISO format). Only used when `DO_ATTENDANCE` is `True`. |
| `ATT_DAYS` | `5` | Number of school days to generate attendance for. Max 180. |
| `ATT_MODE` | `"Section"` | `"Section"` for section-based attendance, `"Daily"` for daily attendance. |

## Edge Cases

`EDGE_CASES` is a list of scenario keys (e.g. `["sc_01", "sc_07"]`). An empty list generates a clean dataset with no edge cases. See [Edge Cases](edge-cases.md) for the full scenario catalog.
