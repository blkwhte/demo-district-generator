# Output Schema

## Directory Structure

Each district generates its own named folder inside `district_data_output/`. Depending on the schema setting, files are organized into `standard/` and/or `anyschool/` subfolders.

```
district_data_output/
└── MapleValley_Data/           # One folder per district
    ├── standard/
    │   ├── schools.csv
    │   ├── teachers.csv
    │   ├── staff.csv
    │   ├── students.csv
    │   ├── sections.csv
    │   ├── enrollments.csv
    │   └── attendance.csv      # Only present when DO_ATTENDANCE = True
    └── anyschool/
        ├── users.csv
        └── sections.csv
```

When 3-day edge case scenarios are enabled, three versioned folders are generated instead of one:

```
district_data_output/
└── MapleValley_Day_1/
└── MapleValley_Day_2/
└── MapleValley_Day_3/
```

The web app automatically zips the entire output directory for download.

---

## Standard Schema

### schools.csv

| Field | Example | Notes |
|---|---|---|
| `School_id` | `sch-a3f9b2` | Prefixed alphanumeric or sequential |
| `School_name` | `Johnson Elementary` | Census last name + school type |
| `School_number` | `01` | Zero-padded index within district |
| `Low_grade` | `KG` | Lowest grade served |
| `High_grade` | `5` | Highest grade served |
| `Principal` | `Sarah Williams` | Synthetic name |
| `Principal_email` | `principal.sch-a3f9b2@maplev...` | Role-based address |
| `School_address` | `142 Oak Street` | Synthetic address |
| `School_city` | `San Francisco` | Real city for the district's state |
| `School_state` | `CA` | State abbreviation |
| `School_zip` | `90043` | Synthetic zip |
| `School_phone` | `415-555-0192` | Synthetic phone |

### teachers.csv

| Field | Example | Notes |
|---|---|---|
| `School_id` | `sch-a3f9b2` | Foreign key to schools |
| `Teacher_id` | `tch-9b4f1a2` | Prefixed alphanumeric or sequential |
| `Teacher_number` | `tch-9b4f` | First 8 chars of Teacher_id |
| `State_teacher_id` | `CA-tch-9b4f` | State prefix + Teacher_number |
| `Teacher_email` | `james.wilson42@...` | Derived from First/Last name |
| `Username` | `james.wilson42` | Derived from First/Last name |
| `First_name` | `James` | Census name pool |
| `Last_name` | `Wilson` | Census name pool |
| `Title` | `Teacher` | |

### staff.csv

| Field | Example | Notes |
|---|---|---|
| `School_id` | `sch-a3f9b2` | |
| `Staff_id` | `stf-b92c441` | Prefixed alphanumeric |
| `Staff_email` | `principal.sch-a3f9b2@...` | Role-based for principals |
| `First_name` | `Sarah` | |
| `Last_name` | `Williams` | |
| `Department` | `Administration` | |
| `Title` | `Principal` | |

### students.csv

| Field | Example | Notes |
|---|---|---|
| `School_id` | `sch-a3f9b2` | |
| `Student_id` | `stu-c2e841` | Prefixed alphanumeric, collision-safe |
| `Student_number` | `stu-c2e8` | First 8 chars of Student_id |
| `State_id` | `CA-stu-c2e8` | State prefix + Student_number |
| `Last_name` | `Rodriguez` | Census name pool |
| `First_name` | `Sofia` | Census name pool |
| `Grade` | `7` | Grade level (`KG`, `1`–`12`) |
| `Gender` | `F` | `M` or `F` |
| `DOB` | `2012-04-15` | Age-appropriate for grade |
| `Student_email` | `sofia.rodriguez31@...` | Derived from First/Last name |
| `Username` | `sofia.rodriguez31` | Derived from First/Last name |
| `Race` | `White` | Weighted random from NCES values |
| `Hispanic_latino` | `Y` | Driven by `PROB_HISPANIC` |
| `Home_language` | `spa` | Correlated with Hispanic_latino |
| `IEP_status` | `N` | `Y` or `N` |
| `FRL_status` | `Y` | `Y` or `N` |
| `ELL_status` | `N` | Derived from Hispanic_latino + Home_language |
| `Section_504_status` | `N` | `Y` or `N` |
| `Gifted_status` | `N` | `Y` or `N` |
| `Disability_status` | `Y` | `Y` or `N` |
| `Disability_type` | `Autism` | Only populated when Disability_status = Y |
| `Disability_code` | `AUT` | `AUT`, `SLD`, or `SLI` |
| `ext.locker_number` | `` | Populated when DO_EXTENSIONS = True |
| `ext.bus_route` | `` | Populated when DO_EXTENSIONS = True |
| `Contact_relationship` | `Mother` | Populated when DO_CONTACTS = True |
| `Contact_type` | `Parent/Guardian` | |
| `Contact_name` | `Maria Rodriguez` | Shares student's last name |
| `Contact_phone` | `415-555-0134` | |
| `Contact_phone_type` | `Cell` | |
| `Contact_email` | `maria.rodriguez@example.com` | |
| `Contact_sis_id` | `cont-a3f9b200` | |

### sections.csv

| Field | Example | Notes |
|---|---|---|
| `School_id` | `sch-a3f9b2` | |
| `Section_id` | `sec-f1a29b34` | Prefixed alphanumeric, collision-safe |
| `Teacher_id` | `tch-9b4f1a2` | Foreign key to teachers |
| `Teacher_2_id` | `` | Empty by default |
| `Name` | `7 - Math` | Grade + Subject |
| `Course_name` | `Algebra 1` | From course catalog |
| `Course_number` | `MATH-07` | From course catalog |
| `Course_description` | `Linear equations, inequalities...` | From course catalog |
| `Grade` | `7` | |
| `Subject` | `Math` | |
| `Term_name` | `Sem 1 2025` | |
| `Term_start` | `2025-08-15` | |
| `Term_end` | `2025-12-20` | |
| `Period` | `3` | Period number within the teacher's day |

### enrollments.csv

| Field | Example |
|---|---|
| `School_id` | `sch-a3f9b2` |
| `Section_id` | `sec-f1a29b34` |
| `Student_id` | `stu-c2e841` |

### attendance.csv

Only generated when `DO_ATTENDANCE = True`.

| Field | Example | Notes |
|---|---|---|
| `Attendance_id` | `att-...` | |
| `School_id` | `sch-a3f9b2` | |
| `Student_id` | `stu-c2e841` | |
| `Section_id` | `sec-f1a29b34` | Present in Section mode |
| `Attendance_date` | `2025-09-01` | |
| `Attendance_status` | `present` | |
| `Attendance_type` | `Section` or `Daily` | Matches ATT_MODE |
| `Excuse_code` | `` | Populated for excused absences |

---

## AnySchool Schema

### users.csv

A unified file combining students, teachers, and staff into a single user list.

| Field | Notes |
|---|---|
| `School_name` | Human-readable school name |
| `User_type` | `student`, `teacher`, or `staff` |
| `User_id` | Original ID from standard schema |
| `First_name` | |
| `Last_name` | |
| `Email` | |
| `Username` | |
| `Grade` | Students only; grade values mapped (`KG` → `Kindergarten`) |
| `DOB` | Students only; formatted as `MM/DD/YYYY` |

### anyschool/sections.csv

One row per student enrollment, denormalized with section metadata.

| Field | Notes |
|---|---|
| `School_name` | |
| `Section_id` | |
| `User_id` | Student ID |
| `Teacher_id` | |
| `School_number` | |
| `Subject` | Mapped to AnySchool values (e.g. `ELA` → `english/language arts`) |
| `Period` | |
| `Section_name` | |

### AnySchool Subject Mappings

| Internal | AnySchool |
|---|---|
| `Math` | `math` |
| `Science` | `science` |
| `ELA` | `english/language arts` |
| `History` | `social studies` |
| `Art` | `arts and music` |
| `PE` | `pe and health` |
| `Summer Math` | `math` |
| `Summer Reading` | `english/language arts` |
| `Summer Credit Recovery` | `other` |

---

## Edge Case Report

When any edge cases are enabled, a `{DistrictName}_edge_cases_report.txt` file is written alongside the data folders. It lists every active scenario and the specific record IDs affected, making it easy to locate the injected anomalies during testing.
