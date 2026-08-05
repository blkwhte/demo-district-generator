# Edge Cases

The generator includes 39 individually toggleable edge case scenarios for testing how downstream applications handle unusual or malformed data. Scenarios are grouped into two categories.

Edge cases are selected in the web app via two expander panels below Advanced Settings, or in the CLI via an interactive prompt. When any 3-day scenario is selected, the output automatically uses a Day 1 / Day 2 / Day 3 folder structure instead of a single Data folder.

An edge case report file (`{DistrictName}_edge_cases_report.txt`) is written alongside the output when any scenarios are active, listing the specific record IDs affected by each scenario.

---

## Static Scenarios

These work in a standard single-day dataset. They can be combined freely with each other and with 3-day scenarios.

| # | Label | Description |
|---|---|---|
| 1 | Teachers in Multiple Schools | A teacher record appears in more than one school within the same district. |
| 2 | Students in Multiple Schools | A student record appears in more than one school within the same district. |
| 3 | Admins in Multiple Schools | A staff/admin record appears in more than one school within the same district. |
| 4 | Nonsense Section Name | A small number of sections are given a random numeric string as their name. |
| 5 | Non-unique Section Names | Multiple sections share the generic name "Homeroom". |
| 6 | Section without Teacher | A small number of sections have no `Teacher_id` assigned. |
| 8 | Unexpected Characters in Email | A small number of student emails contain unexpected characters (e.g. apostrophe). |
| 9 | Missing @ in Email | A small number of student emails are malformed with the @ symbol removed. |
| 10 | Special Characters in Name | Some students have last names containing special characters (e.g. O'Connor, Nuñez). |
| 11 | Student Name Max Char Limit | Some students have an extremely long last name to test field length handling. |
| 12 | Short Name | Some students have a very short last name (e.g. "Li") to test minimum length handling. |
| 13 | Student Section/School Mismatch | A student from School A is enrolled in a section belonging to School B. |
| 14 | Teacher Section/School Mismatch | A teacher from School A is assigned as the teacher of a section belonging to School B. |
| 17 | Student without Enrollments | A student exists in the students file but has no records in the enrollments file. |
| 18 | Teacher without Sections | A teacher exists in the teachers file but is not assigned to any section. |
| 19 | Section ID Max Char Limit | A small number of sections are given an extremely long `Section_id` string. |
| 21 | Section Grade Unmapped | A small number of sections have a grade value not in the standard mapping (e.g. "13"). |
| 22 | Inaccurate Grades | A small number of sections are misclassified with an inaccurate grade (e.g. "PK"). |
| 23 | Split Schools | The last school in the district is duplicated as an "Annex" with a new `School_id`. |
| 24 | Username Char Limits | Some students are given an extremely long username to test field length handling. |
| 25 | Student/Section Grade Mismatch | A student is enrolled in a section whose grade does not match the student's grade. |
| 26 | Unsupported Student Grades | Some students are assigned an unsupported grade value (e.g. "-1"). |
| 28 | No Username | Some students have an empty `Username` field. |
| 29 | Student/Teacher Matching SIS ID | A student is given the same SIS ID as an existing teacher. |
| 32 | Terms Not in Session | A small number of sections are assigned term dates far in the future. |
| 35 | Teacher with No Student Mapping | One teacher is given sections that receive zero enrollments, so no students are associated with them. |
| 36 | Student Associated with Only One Teacher | One student is enrolled exclusively in sections belonging to a single teacher. |
| 37 | Teachers Spanning Same and Different Schools | Two teachers are duplicated into a second school, creating contrast between single-school and multi-school teachers in the same dataset. |
| 38 | Section with Large Enrollment (50+ Students) | One section is force-enrolled with 50 students to test handling of oversized rosters. |
| 39 | Section with Minimal Enrollment (1-2 Students) | One section has its enrollment stripped down to exactly 1-2 students to test near-empty roster handling. |

---

## 3-Day Rotation Scenarios

These scenarios require a 3-day SFTP rotation structure. When any of these are selected, the generator produces three output folders (`Day_1`, `Day_2`, `Day_3`) representing successive daily SFTP drops. Each day's folder contains a complete snapshot of the district roster with the mutations for that day applied.

| # | Label | Description |
|---|---|---|
| 7 | SFTP Username Overwrite | On Day 2, a student's username is changed to simulate an SFTP overwrite scenario. |
| 15 | Student Deleted Day 2, Restored Day 3 | A student is removed from the roster on Day 2, then re-added on Day 3. |
| 16 | Section Deleted Day 2, Restored Day 3 | A section is removed from the roster on Day 2, then re-added on Day 3. |
| 20 | Section Moves to New School (Day 3) | On Day 3, a section's `School_id` is changed to a different school. |
| 27 | SIS ID Changes Day 2, Reverts Day 3 | A student's SIS ID is changed on Day 2 then reverted to the original on Day 3. |
| 30 | Contact ID Changes Day 2 | On Day 2, a student's `Contact_sis_id` is changed to a new value. |
| 31 | Contact Type Inconsistent Day 2 | On Day 2, a student's `Contact_type` is changed to a non-standard value ("Neighbor"). |
| 33 | Student Transfers School (Day 3) | On Day 3, a student's `School_id` is changed to a different school and their enrollments are cleared. |
| 34 | Teacher Transfers School (Day 3) | On Day 3, a teacher's `School_id` is changed to a different school. |

---

## Combining Scenarios

Static and 3-day scenarios can be freely combined in a single run. For example, enabling Sc 13 (Student Section/School Mismatch) alongside Sc 15 (Student Deleted Day 2) will inject both anomalies — the mismatch will be present in all three day snapshots, while the deletion will occur in Day 2 and the restoration in Day 3.

The edge case report identifies which specific record IDs were affected by each scenario, making it straightforward to locate the injected data during testing.

---

## Adding New Scenarios

New scenarios are added to the `EDGE_CASE_REGISTRY` list in `generator_core.py`. Each entry requires:

```python
{
    "key": "sc_40",              # Unique key, zero-padded
    "number": 40,                # Sequential number
    "label": "Short label",      # Shown in the UI
    "description": "...",        # Shown as a tooltip in the web app
    "requires_3_day": False      # True if this needs Day 1/2/3 structure
}
```

The web app and CLI pick up new scenarios automatically from the registry — no changes to `app.py` or `cli.py` are needed.
