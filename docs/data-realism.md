# Data Realism

This document explains the design decisions behind how the generator produces realistic-looking data at scale — covering name generation, demographic correlation, school type distribution, and the course catalog.

---

## Name Generation

### The Problem with Faker

The tool uses [Faker](https://faker.readthedocs.io/) for addresses, phone numbers, and dates of birth. However, Faker's `en_US` locale uses a **frequency-weighted** name distribution that mirrors real-world US name popularity. This means "Smith" and "Michael" are sampled far more often than rarer names. At 281,000 students, "Smith" appeared 6,019 times (2.14% of the dataset) — visually jarring when browsing the data.

### Census Name Engine

Name generation uses a custom pool sourced from public domain data:

- **Surnames:** US Census Bureau 2010 surname frequency list — 639 surnames
- **First names:** SSA baby name data aggregated 1990–2020 — 200 female + 200 male = 400 first names

All names are sampled with **uniform probability** (every name equally likely). This means no single name dominates:

| Scale | Faker "Smith" frequency | Census engine top surname |
|---|---|---|
| 5,000 students | ~107 times (2.1%) | ~7 times (0.14%) |
| 50,000 students | ~1,070 times (2.1%) | ~72 times (0.14%) |
| 281,000 students | ~6,019 times (2.1%) | ~405 times (0.14%) |

**Combined pool:** 400 × 639 = **255,600 unique full-name combinations**, with ~15x less repetition of any single name vs. Faker at equivalent scale.

### Name Consistency

Every user's email, username, `First_name`, and `Last_name` are derived from the same single name draw. The generation pattern for all entity types is:

```python
first, last = census_full_name()
username, email = generate_email_username(first, last, domain, fmt)
# first, last, email, username are all used from the same draw
```

Faker is still used for addresses (`fake.street_address()`), phone numbers (`fake.phone_number()`), and dates of birth (`fake.date_between()`).

---

## Demographic Correlation

Three student fields are interdependent and generated together using a cascade model, rather than three independent random draws. This prevents impossible combinations like a student with `Home_language = spa` but `Hispanic_latino = N` and `ELL_status = N`.

### The Cascade

**Step 1 — Hispanic/Latino identity**
Sampled against `PROB_HISPANIC` (default 0.19, matching the NCES national average for K-12 students).

**Step 2 — Home language**
Spanish's share of the language pool scales proportionally with `PROB_HISPANIC`. At the default 0.19, Spanish accounts for ~20% of the pool. The remaining languages (English, Vietnamese, Chinese, Arabic) maintain their relative proportions.

```
spa_weight = PROB_HISPANIC × 1.05   (slight boost — not all Hispanics speak Spanish at home)
```

**Step 3 — ELL status**
Derived from a probability matrix keyed on the combination of home language and Hispanic identity:

| Home language | Hispanic | ELL probability |
|---|---|---|
| Spanish | Yes | 68% |
| Spanish | No | 45% |
| Other | Yes | 12% |
| Other | No | 3% |

### Cascade at Different Slider Values

At 50,000 students:

| PROB_HISPANIC | Hispanic | Spanish-speaking | ELL |
|---|---|---|---|
| 0.10 | ~10% | ~10% | ~8.5% |
| 0.19 (default) | ~19% | ~20% | ~13.6% |
| 0.35 | ~35% | ~37% | ~23.5% |
| 0.50 | ~50% | ~52% | ~32.8% |

The district-wide ELL rate of ~14% at the default setting is slightly above the NCES national average of 10.6%, which is intentional — the tool is meant to generate interesting test data, not a perfectly average district.

---

## School Type Distribution

### The Problem with Random Selection

With purely random school type selection, a 5-school district might generate 4 High Schools and 1 Elementary — completely unrealistic. At 250 schools with the old logic, 247 of 250 schools were Elementary.

### Pyramid Distribution

School types are now assigned using a ratio-based approach that scales correctly at any district size:

| Type | Target ratio | Grade range |
|---|---|---|
| Elementary | 60% | KG–5 |
| Middle | 20% | 6–8 |
| High | 15% | 9–12 |
| Academy | 5% | KG–12 |

Small districts (1–3 schools) have guaranteed minimums:

| Schools | Distribution |
|---|---|
| 1 | Elementary |
| 2 | Elementary + High |
| 3 | Elementary + Middle + High |
| 4+ | Proportional allocation |

At 250 schools, the generator produces approximately 150 Elementary, 50 Middle, 38 High, and 12 Academy — and the resulting student grade distribution mirrors a real district (~62% elementary, ~21% middle, ~17% high school).

---

## Course Catalog

Sections include three course fields (`Course_name`, `Course_number`, `Course_description`) populated from a built-in catalog of 117 courses keyed on `(subject, grade)`.

### Subjects and Sample Courses

| Subject | KG example | Middle example | High example |
|---|---|---|---|
| Math | Kindergarten Math | Algebra 1 (Gr 7) | AP Calculus AB (Gr 11) |
| ELA | Kindergarten Language Arts | English 7 | AP Literature & Composition (Gr 12) |
| Science | Kindergarten Science | Earth Science (Gr 7) | AP Environmental Science (Gr 12) |
| History | Social Studies - K | World History: Medieval (Gr 7) | AP Government & Politics (Gr 12) |
| Art | Kindergarten Art | Visual Arts 7 | AP Art History (Gr 12) |
| PE | Kindergarten PE | Physical Education 7 | Sports Medicine (Gr 12) |
| Summer Math | Summer Math - K | Summer Algebra 1 (Gr 7) | Summer Calculus (Gr 11) |
| Summer Reading | Summer Reading - K | Summer English 7 | Summer AP Literature (Gr 12) |
| Summer Credit Recovery | Summer Credit Recovery | Summer Credit Recovery | Summer Credit Recovery |

Course names progress realistically with grade level — a grade 6 Math section gets "Pre-Algebra", grade 7 gets "Algebra 1", grade 9 gets "Geometry". Multiple sections sharing the same subject and grade all reference the same catalog entry, creating the realistic pattern of many sections per course.

Unmapped subject/grade combinations (e.g. from edge case grades like "-1" or "13") fall back to a generic name (`{Subject} - Grade {grade}`) rather than crashing.

### Enriching Existing Files

The standalone script `add_courses_to_sections.py` applies the same course catalog to any existing `sections.csv` file:

```bash
python3 add_courses_to_sections.py sections.csv
python3 add_courses_to_sections.py sections.csv --output sections_enriched.csv
python3 add_courses_to_sections.py sections.csv --dry-run
```

---

## ID Design

All alphanumeric IDs use a short entity-type prefix to prevent Excel from misinterpreting hex strings as scientific notation (e.g. bare `9e9554` → Excel renders as `9E+9554`).

| Entity | Format | Example | Unique space |
|---|---|---|---|
| School | `sch-xxxxxx` | `sch-a3f9b2` | 16.7M |
| Teacher | `tch-xxxxxxx` | `tch-f8b4ab5` | 268M |
| Student | `stu-xxxxxx` | `stu-8fe9fa` | 16.7M |
| Section | `sec-xxxxxxxx` | `sec-92617305` | 4.3B |
| Staff | `stf-xxxxxxx` | `stf-9309bbf` | 268M |

A per-district collision guard (`seen_ids` set with retry loop) ensures zero duplicate IDs regardless of district size.
