import os
import random
import uuid
import datetime
import re
import pandas as pd
from faker import Faker


fake = Faker('en_US')  # Retained for addresses, phones, dates — NOT names

# ==========================================
# 0. CENSUS NAME ENGINE
# ==========================================
# Source: US Census Bureau 2010 surname list (public domain)
# Source: SSA baby name data aggregated 1990-2020 (public domain)
# Uniform sampling across 690 surnames x 400 first names = 276,000 unique
# full-name combinations, with ~15x less repetition than Faker's weighted pool.

_CENSUS_LAST_NAMES = [
    "Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Rodriguez","Martinez",
    "Hernandez","Lopez","Gonzalez","Wilson","Anderson","Thomas","Taylor","Moore","Jackson","Martin",
    "Lee","Perez","Thompson","White","Harris","Sanchez","Clark","Ramirez","Lewis","Robinson",
    "Walker","Young","Allen","King","Wright","Scott","Torres","Nguyen","Hill","Flores",
    "Green","Adams","Nelson","Baker","Hall","Rivera","Campbell","Mitchell","Carter","Roberts",
    "Gomez","Phillips","Evans","Turner","Diaz","Parker","Cruz","Edwards","Collins","Reyes",
    "Stewart","Morris","Morales","Murphy","Cook","Rogers","Gutierrez","Ortiz","Morgan","Cooper",
    "Peterson","Bailey","Reed","Kelly","Howard","Ramos","Kim","Cox","Ward","Richardson",
    "Watson","Brooks","Chavez","Wood","James","Bennett","Gray","Mendoza","Ruiz","Hughes",
    "Price","Alvarez","Castillo","Sanders","Patel","Myers","Long","Ross","Foster","Jimenez",
    "Powell","Jenkins","Perry","Russell","Sullivan","Bell","Coleman","Butler","Henderson","Barnes",
    "Gonzales","Fisher","Vasquez","Simmons","Romero","Jordan","Patterson","Alexander","Hamilton","Graham",
    "Reynolds","Griffin","Wallace","Moreno","West","Cole","Hayes","Bryant","Herrera","Gibson",
    "Ellis","Tran","Medina","Aguilar","Stevens","Murray","Ford","Castro","Marshall","Owens",
    "Harrison","Fernandez","Mcdonald","Woods","Washington","Kennedy","Wells","Vargas","Henry","Chen",
    "Freeman","Webb","Tucker","Guzman","Burns","Crawford","Olson","Simpson","Porter","Hunter",
    "Gordon","Mendez","Silva","Shaw","Snyder","Mason","Dixon","Munoz","Hunt","Hicks",
    "Holmes","Palmer","Wagner","Black","Robertson","Boyd","Rose","Stone","Salazar","Fox",
    "Warren","Mills","Meyer","Rice","Schmidt","Garza","Daniels","Ferguson","Nichols","Stephens",
    "Soto","Weaver","Ryan","Gardner","Payne","Grant","Dunn","Kelley","Spencer","Hawkins",
    "Arnold","Pierce","Vazquez","Hansen","Peters","Santos","Hart","Bradley","Knight","Elliott",
    "Cunningham","Duncan","Armstrong","Hudson","Carroll","Lane","Riley","Andrews","Alvarado","Ray",
    "Delgado","Berry","Perkins","Hoffman","Johnston","Matthews","Pena","Richards","Lawrence","Erickson",
    "Horton","Welch","Suarez","Meadows","Lyons","Sandoval","Gould","Day","Schneider","Banks",
    "Bird","Flowers","Roberson","Bates","Hoover","Norris","Sparks","Crane","Caldwell","Reeves",
    "Barker","Gallagher","Harmon","Mcbride","Mann","Garrett","Holt","Fowler","Malone","Pittman",
    "Moody","Acosta","Andersen","Lara","Conner","Larson","Becker","Watkins","George","Owen",
    "Bowen","Obrien","Stein","Swanson","Brady","Rios","Steele","Thornton","Lowe","Ballard",
    "Mccall","Dudley","Mckinney","Gross","Bowman","Cochran","Schroeder","Garner","Gill","Harrington",
    "Cleveland","Holden","Hayden","Ramsey","Morrow","Tanner","Hubbard","Patrick","Oconnor","Stafford",
    "Barber","Strickland","Mccormick","Langley","Kaufman","Ingram","Walton","Rowe","Hampton","Ortega",
    "Patton","Sweeney","Parsons","Mcguire","Rhodes","Frazier","Osborne","Mcclure","Leonard","Rollins",
    "Whitfield","Tillman","Donovan","Hartman","Davison","Haley","Cobb","Greer","Burnett","Wiley",
    "Singleton","Combs","Mack","Oneal","Shields","Macdonald","Cantu","Booth","Jacobs","Sheppard",
    "Merritt","Farrell","Ware","Mcfarland","Benson","Ochoa","Mclaughlin","Duffy","Bowers","Knox",
    "Hess","Olsen","Mcintyre","Luna","Velasquez","Hendrix","Gilmore","Bauer","Calhoun","Decker",
    "Byrd","Osborn","Yates","Mcmahon","Beard","Vega","Alford","Nunez","Hendricks","Mccoy",
    "Bentley","Finley","Mcdaniel","Marsh","Bray","Mcclain","Mahoney","Cline","Wilkins","Mercer",
    "Burnette","Browning","Pratt","Poole","Herring","Glover","Salas","Wyatt","Huber","Holloway",
    "Schaefer","Mcallister","Doyle","Chambers","Brewer","Carey","Mcneil","Stanton","Griffith","Lindsey",
    "Frost","Haynes","Blanchard","Gentry","Mccann","Cowan","Estes","Stout","Contreras","Cardenas",
    "Vance","Bernal","Escobar","Riggs","Wolfe","Holman","Pennington","Mcgowan","Workman","Morin",
    "Pham","Buckley","Zavala","Andrade","Meyers","Odom","Schiller","Crosby","Rivas","Walters",
    "Rosario","Spence","Curry","Moran","Bender","Copeland","Trevino","Ponce","Dyer","Delaney",
    "Compton","Mcnally","Faulkner","Swenson","Whitaker","Morse","Harrell","Hogan","Leblanc","Savage",
    "Dejesus","Yoder","Tomlinson","Arroyo","Nolan","Varner","Shea","Arias","Mata","Lester",
    "Barrera","Zamora","Cisneros","Gallegos","Carver","Villanueva","Salinas","Beltran","Adkins","Mayer",
    "Baxter","Cabrera","Cervantes","Solis","Gilmore","Eaton","Blackwell","Hale","Briggs","Leal",
    "Shannon","Boone","Cortez","Kirby","Madden","Frederick","Huynh","Maldonado","Obrien","Veloz",
    "Cuevas","Arellano","Valencia","Ibarra","Estrada","Acevedo","Figueroa","Guerrero","Reyna","Esparza",
    "Dominguez","Vela","Molina","Serrano","Trujillo","Orozco","Tapia","Solano","Deleon","Montes",
    "Ybarra","Palacios","Cano","Cordova","Fuentes","Lozano","Vidal","Meza","Ledesma","Ayala",
    "Rangel","Montoya","Nava","Quintero","Fonseca","Duarte","Carrillo","Cardona","Blanco","Mercado",
    "Frye","Mcgee","Haas","Bowden","Oswald","Hinton","Kemp","Allison","Sharpe","Petersen",
    "Lowery","Hayward","Pitts","Dunlap","Bridges","Anthony","Wolf","Church","Mcrae","Stokes",
    "Blackburn","Pollard","Norwood","Humphrey","Atkins","Randolph","Pruitt","Barlow","Mosley","Christensen",
    "Oneil","Hartley","Noel","Haney","Dunbar","Swain","Hanna","Coffey","Sloan","Galloway",
    "Hester","Kern","Voss","Shepard","Wilcox","Parrish","Whitley","Barton","Sexton","Mcpherson",
    "Hobbs","Kerr","Woodward","Mcmillan","Alston","Hines","Pugh","Booker","Hooper","Robins",
    "Mcintosh","Sherrill","Moffitt","Hagan","Sears","Hardwick","Beaumont","Yuen","Leung","Nakamura",
    "Andersen","Johansson","Eriksson","Oconnell","Fitzgerald","Flanagan","Kowalski","Novak","Dvorak",
    "Malik","Khan","Sheikh","Chaudhry","Siddiqui","Ibrahim","Hassan","Ali","Ahmed","Hussain",
    "Choi","Park","Jung","Jeon","Kwon","Shin","Han","Lim","Yoon","Oh",
    "Diallo","Traore","Coulibaly","Camara","Toure","Diop","Cisse","Dembele","Sylla","Bah",
]

_CENSUS_FIRST_NAMES_FEMALE = [
    "Mary","Patricia","Jennifer","Linda","Barbara","Elizabeth","Susan","Jessica","Sarah","Karen",
    "Lisa","Nancy","Betty","Margaret","Sandra","Ashley","Dorothy","Kimberly","Emily","Donna",
    "Michelle","Carol","Amanda","Melissa","Deborah","Stephanie","Rebecca","Sharon","Laura","Cynthia",
    "Kathleen","Amy","Angela","Shirley","Anna","Brenda","Pamela","Emma","Nicole","Helen",
    "Samantha","Katherine","Christine","Debra","Rachel","Carolyn","Janet","Catherine","Maria","Heather",
    "Diane","Julie","Joyce","Victoria","Kelly","Christina","Lauren","Joan","Evelyn","Olivia",
    "Judith","Megan","Cheryl","Andrea","Hannah","Martha","Jacqueline","Frances","Gloria","Ann",
    "Teresa","Kathryn","Sara","Janice","Jean","Alice","Madison","Doris","Abigail","Julia",
    "Grace","Denise","Amber","Marilyn","Beverly","Danielle","Theresa","Sophia","Marie","Diana",
    "Brittany","Natalie","Isabella","Charlotte","Rose","Alexis","Kayla","Lori","Tiffany","Vanessa",
    "Brittney","Jasmine","Alyssa","Alexandria","Bailey","Haley","Crystal","Destiny","Sierra","Savannah",
    "Autumn","Cassandra","Miranda","Hailey","Taylor","Brooke","Courtney","Paige","Morgan","Kylie",
    "Leah","Chloe","Kennedy","Peyton","Mackenzie","Aaliyah","Riley","Zoey","Avery","Aubrey",
    "Lily","Addison","Gabriella","Layla","Sofia","Natalia","Arianna","Mia","Lillian","Zoe",
    "Claire","Audrey","Scarlett","Allison","Elena","Madeline","Ellie","Naomi","Maya","Kaylee",
    "Lydia","Nora","Camille","Stella","Eva","Eliana","Violet","Brooklyn","Paisley","Sadie",
    "Piper","Willow","Ariel","Aurora","Brianna","Jade","Sienna","Penelope","Delilah","Skylar",
    "Nadia","Faith","Serenity","Vivian","Aria","Phoebe","Brielle","Juliana","Rebekah","Valeria",
    "Mariana","Selena","Trinity","Luna","Adriana","Amelia","Mila","Freya","Celeste","Lila",
    "Iris","Vera","June","Wren","Fiona","Clara","Demi","Aisha","Imani","Camila",
]

_CENSUS_FIRST_NAMES_MALE = [
    "James","John","Robert","Michael","William","David","Richard","Joseph","Thomas","Charles",
    "Christopher","Daniel","Matthew","Anthony","Mark","Donald","Steven","Paul","Andrew","Joshua",
    "Kenneth","Kevin","Brian","George","Timothy","Ronald","Edward","Jason","Jeffrey","Ryan",
    "Jacob","Gary","Nicholas","Eric","Jonathan","Stephen","Larry","Justin","Scott","Brandon",
    "Benjamin","Samuel","Raymond","Gregory","Frank","Alexander","Patrick","Jack","Dennis","Jerry",
    "Tyler","Aaron","Jose","Henry","Adam","Douglas","Nathan","Peter","Zachary","Kyle",
    "Walter","Harold","Jeremy","Ethan","Carl","Keith","Roger","Gerald","Christian","Terry",
    "Sean","Arthur","Austin","Noah","Lawrence","Jesse","Joe","Bryan","Billy","Jordan",
    "Albert","Dylan","Bruce","Willie","Gabriel","Alan","Juan","Logan","Wayne","Roy",
    "Ralph","Randy","Eugene","Vincent","Russell","Louis","Philip","Bobby","Johnny","Bradley",
    "Mason","Caleb","Carlos","Miguel","Elijah","Liam","Aiden","Lucas","Jackson","Owen",
    "Jayden","Connor","Brayden","Evan","Isaiah","Landon","Cameron","Hunter","Dominic","Charlie",
    "Eli","Julian","Chase","Marcus","Cole","Levi","Luke","Nathan","Ian","Sebastian",
    "Xavier","Gavin","Nolan","Hudson","Bryson","Colton","Jaxson","Jeremiah","Bryce","Easton",
    "Miles","Sawyer","Damian","Ryder","Maxwell","Tristan","Ivan","Ezra","Bentley","Silas",
    "Santiago","Declan","Axel","Preston","Emmett","Jase","Mateo","Greyson","Weston","Knox",
    "Bennett","Corbin","Josiah","Asher","Felix","Hayden","Tanner","Reid","Beau","Griffin",
    "Jasper","Kayden","Zion","Jaxon","Elliot","Ryker","Phoenix","Rowan","Finn","Rhett",
    "Atticus","Zane","Malcolm","Archer","Beckett","Caden","Drake","Gage","Grayson","Holden",
    "Jace","Maddox","Nico","Orion","Paxton","Quentin","Remington","Sterling","Theo","Omar",
]

_ALL_FIRST_NAMES = _CENSUS_FIRST_NAMES_FEMALE + _CENSUS_FIRST_NAMES_MALE

def census_first_name(gender=None):
    """Return a random first name. gender='M', 'F', or None for either."""
    if gender == 'F':
        return random.choice(_CENSUS_FIRST_NAMES_FEMALE)
    elif gender == 'M':
        return random.choice(_CENSUS_FIRST_NAMES_MALE)
    return random.choice(_ALL_FIRST_NAMES)

def census_last_name():
    """Return a random last name from the Census pool."""
    return random.choice(_CENSUS_LAST_NAMES).capitalize()

def census_full_name(gender=None):
    """Return a (first, last) tuple."""
    return census_first_name(gender), census_last_name()


# ==========================================
# 1. CONSTANTS & DEFAULTS
# ==========================================
DEFAULTS = {
    "ID_MODE": "alphanumeric",
    "OUTPUT_FORMAT": "csv",
    "OUTPUT_SCHEMA": "standard",
    "EMAIL_DOMAIN": "",
    "USERNAME_FMT": "first.last",
    "NUM_DISTRICTS": 1,
    "SCHOOLS_PER_DISTRICT": 5,
    "TEACHERS_PER_SCHOOL": "15-30",
    "STUDENTS_PER_SECTION": "18-32",
    "SECTIONS_PER_TEACHER_TERM": 5,
    "SCHOOL_START_YEAR": "2025",
    "NUM_TERMS": 2,
    "INCLUDE_SUMMER": True,
    "PROB_FRL": 0.45,
    "PROB_IEP": 0.12,
    "PROB_HISPANIC": 0.19,  # National average ~19% (NCES 2023). Drives Home_language and ELL cascade.
    "PROB_504": 0.05,
    "PROB_GIFTED": 0.08,
    "PROB_DISABILITY": 0.11,
    "DO_EXTENSIONS": False,
    "DO_CONTACTS": True,
    "DO_RESOURCES": False,
    "DO_ATTENDANCE": False,
    "ATT_START_DATE": "2025-09-01",
    "ATT_DAYS": 5,
    "ATT_MODE": "Section",
    "EDGE_CASES": []  # List of scenario keys, e.g. ["sc_01", "sc_07"]. Empty = no edge cases.
}

# ==========================================
# 2. EDGE CASE REGISTRY
# ==========================================
# Each entry: key, number, label, description, requires_3_day
EDGE_CASE_REGISTRY = [
    # --- Static Scenarios (work in a single-day dataset) ---
    {
        "key": "sc_01", "number": 1,
        "label": "Teachers in Multiple Schools",
        "description": "A teacher record appears in more than one school within the same district.",
        "requires_3_day": False
    },
    {
        "key": "sc_02", "number": 2,
        "label": "Students in Multiple Schools",
        "description": "A student record appears in more than one school within the same district.",
        "requires_3_day": False
    },
    {
        "key": "sc_03", "number": 3,
        "label": "Admins in Multiple Schools",
        "description": "A staff/admin record appears in more than one school within the same district.",
        "requires_3_day": False
    },
    {
        "key": "sc_04", "number": 4,
        "label": "Nonsense Section Name",
        "description": "A small number of sections are given a random numeric string as their name.",
        "requires_3_day": False
    },
    {
        "key": "sc_05", "number": 5,
        "label": "Non-unique Section Names",
        "description": "Multiple sections share the generic name 'Homeroom'.",
        "requires_3_day": False
    },
    {
        "key": "sc_06", "number": 6,
        "label": "Section without Teacher",
        "description": "A small number of sections have no Teacher_id assigned.",
        "requires_3_day": False
    },
    {
        "key": "sc_07", "number": 7,
        "label": "SFTP Username Overwrite",
        "description": "On Day 2, a student's username is changed to simulate an SFTP overwrite scenario.",
        "requires_3_day": True
    },
    {
        "key": "sc_08", "number": 8,
        "label": "Unexpected Characters in Email",
        "description": "A small number of student emails contain unexpected characters (e.g. apostrophe).",
        "requires_3_day": False
    },
    {
        "key": "sc_09", "number": 9,
        "label": "Missing @ in Email",
        "description": "A small number of student emails are malformed with the @ symbol removed.",
        "requires_3_day": False
    },
    {
        "key": "sc_10", "number": 10,
        "label": "Special Characters in Name",
        "description": "Some students have last names containing special characters (e.g. O'Connor, Nuñez).",
        "requires_3_day": False
    },
    {
        "key": "sc_11", "number": 11,
        "label": "Student Name Max Char Limit",
        "description": "Some students have an extremely long last name to test field length handling.",
        "requires_3_day": False
    },
    {
        "key": "sc_12", "number": 12,
        "label": "Short Name",
        "description": "Some students have a very short last name (e.g. 'Li') to test minimum length handling.",
        "requires_3_day": False
    },
    {
        "key": "sc_13", "number": 13,
        "label": "Student Section/School Mismatch",
        "description": "A student from School A is enrolled in a section belonging to School B.",
        "requires_3_day": False
    },
    {
        "key": "sc_14", "number": 14,
        "label": "Teacher Section/School Mismatch",
        "description": "A teacher from School A is assigned as the teacher of a section belonging to School B.",
        "requires_3_day": False
    },
    {
        "key": "sc_15", "number": 15,
        "label": "Student Deleted Day 2, Restored Day 3",
        "description": "A student is removed from the roster on Day 2, then re-added on Day 3.",
        "requires_3_day": True
    },
    {
        "key": "sc_16", "number": 16,
        "label": "Section Deleted Day 2, Restored Day 3",
        "description": "A section is removed from the roster on Day 2, then re-added on Day 3.",
        "requires_3_day": True
    },
    {
        "key": "sc_17", "number": 17,
        "label": "Student without Enrollments",
        "description": "A student exists in the students file but has no records in the enrollments file.",
        "requires_3_day": False
    },
    {
        "key": "sc_18", "number": 18,
        "label": "Teacher without Sections",
        "description": "A teacher exists in the teachers file but is not assigned to any section.",
        "requires_3_day": False
    },
    {
        "key": "sc_19", "number": 19,
        "label": "Section ID Max Char Limit",
        "description": "A small number of sections are given an extremely long Section_id string.",
        "requires_3_day": False
    },
    {
        "key": "sc_20", "number": 20,
        "label": "Section Moves to New School (Day 3)",
        "description": "On Day 3, a section's School_id is changed to a different school.",
        "requires_3_day": True
    },
    {
        "key": "sc_21", "number": 21,
        "label": "Section Grade Unmapped",
        "description": "A small number of sections have a grade value not in the standard mapping (e.g. '13').",
        "requires_3_day": False
    },
    {
        "key": "sc_22", "number": 22,
        "label": "Inaccurate Grades",
        "description": "A small number of sections are misclassified with an inaccurate grade (e.g. 'PK').",
        "requires_3_day": False
    },
    {
        "key": "sc_23", "number": 23,
        "label": "Split Schools",
        "description": "The last school in the district is duplicated as an 'Annex' with a new School_id.",
        "requires_3_day": False
    },
    {
        "key": "sc_24", "number": 24,
        "label": "Username Char Limits",
        "description": "Some students are given an extremely long username to test field length handling.",
        "requires_3_day": False
    },
    {
        "key": "sc_25", "number": 25,
        "label": "Student/Section Grade Mismatch",
        "description": "A student is enrolled in a section whose grade does not match the student's grade.",
        "requires_3_day": False
    },
    {
        "key": "sc_26", "number": 26,
        "label": "Unsupported Student Grades",
        "description": "Some students are assigned an unsupported grade value (e.g. '-1').",
        "requires_3_day": False
    },
    {
        "key": "sc_27", "number": 27,
        "label": "SIS ID Changes Day 2, Reverts Day 3",
        "description": "A student's SIS ID is changed on Day 2 then reverted to the original on Day 3.",
        "requires_3_day": True
    },
    {
        "key": "sc_28", "number": 28,
        "label": "No Username",
        "description": "Some students have an empty Username field.",
        "requires_3_day": False
    },
    {
        "key": "sc_29", "number": 29,
        "label": "Student/Teacher Matching SIS ID",
        "description": "A student is given the same SIS ID as an existing teacher.",
        "requires_3_day": False
    },
    {
        "key": "sc_30", "number": 30,
        "label": "Contact ID Changes Day 2",
        "description": "On Day 2, a student's Contact_sis_id is changed to a new value.",
        "requires_3_day": True
    },
    {
        "key": "sc_31", "number": 31,
        "label": "Contact Type Inconsistent Day 2",
        "description": "On Day 2, a student's Contact_type is changed to a non-standard value ('Neighbor').",
        "requires_3_day": True
    },
    {
        "key": "sc_32", "number": 32,
        "label": "Terms Not in Session",
        "description": "A small number of sections are assigned term dates far in the future.",
        "requires_3_day": False
    },
    {
        "key": "sc_33", "number": 33,
        "label": "Student Transfers School (Day 3)",
        "description": "On Day 3, a student's School_id is changed to a different school and their enrollments are cleared.",
        "requires_3_day": True
    },
    {
        "key": "sc_34", "number": 34,
        "label": "Teacher Transfers School (Day 3)",
        "description": "On Day 3, a teacher's School_id is changed to a different school.",
        "requires_3_day": True
    },
    {
        "key": "sc_35", "number": 35,
        "label": "Teacher assigned to Section without Student Enrollments",
        "description": "One teacher is given sections that receive zero enrollments, so no students are associated with them.",
        "requires_3_day": False
    },
    {
        "key": "sc_36", "number": 36,
        "label": "Student associated with only one Teacher",
        "description": "One student is enrolled exclusively in sections belonging to a single teacher.",
        "requires_3_day": False
    },
    {
        "key": "sc_37", "number": 37,
        "label": "Teachers Spanning Same and Different Schools",
        "description": "Two teachers are duplicated into a second school, creating contrast between single-school and multi-school teachers in the same dataset.",
        "requires_3_day": False
    },
    {
        "key": "sc_38", "number": 38,
        "label": "Section with Large Enrollment (50+ Students)",
        "description": "One section is force-enrolled with 50 students to test handling of oversized rosters.",
        "requires_3_day": False
    },
    {
        "key": "sc_39", "number": 39,
        "label": "Section with Minimal Enrollment (1-2 Students)",
        "description": "One section has its enrollment stripped down to exactly 1-2 students to test near-empty roster handling.",
        "requires_3_day": False
    },
]

# Convenience lookups
EC_BY_KEY = {ec["key"]: ec for ec in EDGE_CASE_REGISTRY}
STATIC_CASES = [ec for ec in EDGE_CASE_REGISTRY if not ec["requires_3_day"]]
THREE_DAY_CASES = [ec for ec in EDGE_CASE_REGISTRY if ec["requires_3_day"]]


def get_active_cases(config):
    """Return the set of active scenario keys from config, and whether 3-day mode is needed."""
    selected = set(config.get("EDGE_CASES", []))
    needs_3_day = any(EC_BY_KEY[k]["requires_3_day"] for k in selected if k in EC_BY_KEY)
    return selected, needs_3_day



def get_school_type_sequence(num_schools):
    """
    Return a realistic, shuffled list of school types for a district
    that scales correctly at any size.

    Target ratios (mirroring real US district composition):
      Elementary : 60%  (KG-5)
      Middle     : 20%  (6-8)
      High       : 15%  (9-12)
      Academy    :  5%  (KG-12)

    Small-district guarantees:
      1  → [Elementary]
      2  → [Elementary, High]
      3  → [Elementary, Middle, High]
      4+ → proportional allocation, always at least 1 of each core type
    """
    if num_schools == 1:
        return ["Elementary"]
    if num_schools == 2:
        return ["Elementary", "High"]
    if num_schools == 3:
        return random.sample(["Elementary", "Middle", "High"], 3)
    ratios = {"Elementary": 0.60, "Middle": 0.20, "High": 0.15, "Academy": 0.05}
    counts = {t: max(1, round(num_schools * r)) for t, r in ratios.items()}
    diff = num_schools - sum(counts.values())
    counts["Elementary"] += diff
    sequence = []
    for school_type, count in counts.items():
        sequence.extend([school_type] * count)
    random.shuffle(sequence)
    return sequence

GENERIC_DISTRICT_NAMES = ["MapleValley", "OakRiver", "SummitHeights", "PineCreek", "LibertyUnion", "Heritage", "PioneerValley", "GrandView", "Clearwater", "HopeSprings", "NorthStar", "GoldenPlains", "SilverLake", "WillowCreek", "Unity", "CedarRidge"]
STATE_MAPPINGS = {"C4a": ("California", "CA"), "T3x": ("Texas", "TX"), "N3y": ("New York", "NY"), "F1a": ("Florida", "FL"), "W2a": ("Washington", "WA"), "I1l": ("Illinois", "IL"), "C0l": ("Colorado", "CO"), "A7z": ("Arizona", "AZ"), "G4a": ("Georgia", "GA"), "M4a": ("Massachusetts", "MA")}
STATE_KEYS = list(STATE_MAPPINGS.keys())
REAL_LOCATIONS = {"CA": [("San Francisco", "941"), ("Los Angeles", "900")], "TX": [("Austin", "787"), ("Dallas", "752")], "NY": [("New York", "100"), ("Brooklyn", "112")], "FL": [("Miami", "331"), ("Orlando", "328")]}
CLEVER_RACE_VALUES = ["White", "Black or African American", "Asian", "American Indian or Alaska Native", "Native Hawaiian or Other Pacific Islander", "Two or more races", "Unknown"]
RACE_WEIGHTS = [0.50, 0.15, 0.06, 0.02, 0.01, 0.06, 0.20]
LANG_KEYS = ["eng", "spa", "vie", "zho", "ara"]

def get_lang_weights(prob_hispanic):
    """
    Derive language-pool weights from the Hispanic/Latino prevalence setting.
    Spanish share scales with PROB_HISPANIC; remaining non-Spanish shares
    are kept proportional to their baseline values.
    Baseline (prob_hispanic=0.19): spa≈0.20, others share 0.80
    """
    spa_weight = round(prob_hispanic * 1.05, 4)   # ~5% of Hispanic students speak a non-Spanish language
    spa_weight = max(0.01, min(0.95, spa_weight))  # clamp to [0.01, 0.95]
    other_total = 1.0 - spa_weight
    # Baseline non-Spanish proportions: eng=0.875, vie=0.0625, zho=0.0375, ara=0.025
    eng = round(other_total * 0.875, 4)
    vie = round(other_total * 0.0625, 4)
    zho = round(other_total * 0.0375, 4)
    ara = round(other_total * 0.025, 4)
    return [eng, spa_weight, vie, zho, ara]

# ELL probability matrix — correlated with Home_language and Hispanic_latino
# Keys: (is_spanish_speaker, is_hispanic)
ELL_PROB_MATRIX = {
    (True,  True):  0.68,   # Spanish-speaking Hispanic: highest ELL rate
    (True,  False): 0.45,   # Spanish-speaking non-Hispanic: still likely ELL
    (False, True):  0.12,   # Hispanic, non-Spanish: some ELL need
    (False, False): 0.03,   # General population baseline
}

# ==========================================
# COURSE CATALOG
# ==========================================
# One canonical course per (subject, grade) combination.
# Sections reference this catalog via course_name, course_number,
# and course_description — no separate courses file needed.
# Keyed as (subject, grade_string).

COURSE_CATALOG = {
    # --- MATH ---
    ("Math", "KG"): ("Kindergarten Math",            "MATH-KG", "Foundational number sense, counting, and basic shapes."),
    ("Math", "1"):  ("Grade 1 Math",                 "MATH-01", "Addition, subtraction, and introduction to place value."),
    ("Math", "2"):  ("Grade 2 Math",                 "MATH-02", "Multi-digit addition and subtraction, measurement, and data."),
    ("Math", "3"):  ("Grade 3 Math",                 "MATH-03", "Multiplication, division, fractions, and area."),
    ("Math", "4"):  ("Grade 4 Math",                 "MATH-04", "Multi-digit multiplication, fraction equivalence, and decimals."),
    ("Math", "5"):  ("Grade 5 Math",                 "MATH-05", "Fractions, decimals, and introduction to coordinate systems."),
    ("Math", "6"):  ("Pre-Algebra",                  "MATH-06", "Ratios, proportional relationships, and introduction to algebra."),
    ("Math", "7"):  ("Algebra 1",                    "MATH-07", "Linear equations, inequalities, and functions."),
    ("Math", "8"):  ("Algebra 2",                    "MATH-08", "Quadratic functions, polynomials, and systems of equations."),
    ("Math", "9"):  ("Geometry",                     "MATH-09", "Congruence, similarity, trigonometry, and proof."),
    ("Math", "10"): ("Pre-Calculus",                 "MATH-10", "Trigonometric functions, vectors, and limits."),
    ("Math", "11"): ("AP Calculus AB",               "MATH-11", "Differential and integral calculus with applications."),
    ("Math", "12"): ("AP Calculus BC",               "MATH-12", "Advanced integration techniques, series, and parametric equations."),

    # --- ELA ---
    ("ELA", "KG"): ("Kindergarten Language Arts",    "ELA-KG",  "Phonics, print concepts, and foundational reading skills."),
    ("ELA", "1"):  ("Grade 1 Language Arts",         "ELA-01",  "Phonics, fluency, and beginning reading comprehension."),
    ("ELA", "2"):  ("Grade 2 Language Arts",         "ELA-02",  "Reading comprehension, writing conventions, and vocabulary."),
    ("ELA", "3"):  ("Grade 3 Language Arts",         "ELA-03",  "Literature analysis, informational text, and narrative writing."),
    ("ELA", "4"):  ("Grade 4 Language Arts",         "ELA-04",  "Opinion writing, research skills, and literary analysis."),
    ("ELA", "5"):  ("Grade 5 Language Arts",         "ELA-05",  "Figurative language, text structure, and argumentative writing."),
    ("ELA", "6"):  ("English 6",                     "ELA-06",  "Fiction and nonfiction analysis, essay writing, and grammar."),
    ("ELA", "7"):  ("English 7",                     "ELA-07",  "Literary themes, research writing, and oral communication."),
    ("ELA", "8"):  ("English 8",                     "ELA-08",  "Argumentative writing, close reading, and language conventions."),
    ("ELA", "9"):  ("English 9",                     "ELA-09",  "World literature, narrative writing, and rhetorical analysis."),
    ("ELA", "10"): ("English 10",                    "ELA-10",  "American literature, analytical essays, and seminar discussion."),
    ("ELA", "11"): ("AP Language & Composition",     "ELA-11",  "Rhetorical analysis, synthesis essays, and argumentation."),
    ("ELA", "12"): ("AP Literature & Composition",   "ELA-12",  "Literary analysis, poetry, drama, and extended essay."),

    # --- SCIENCE ---
    ("Science", "KG"): ("Kindergarten Science",      "SCI-KG",  "Observation, weather, plants, animals, and basic earth science."),
    ("Science", "1"):  ("Grade 1 Science",           "SCI-01",  "Matter, motion, living things, and seasonal changes."),
    ("Science", "2"):  ("Grade 2 Science",           "SCI-02",  "Ecosystems, forces, landforms, and weather patterns."),
    ("Science", "3"):  ("Grade 3 Science",           "SCI-03",  "Life cycles, habitats, forces, and weather data."),
    ("Science", "4"):  ("Grade 4 Science",           "SCI-04",  "Energy, waves, Earth processes, and organisms."),
    ("Science", "5"):  ("Grade 5 Science",           "SCI-05",  "Matter and energy, ecosystems, and Earth systems."),
    ("Science", "6"):  ("Life Science",              "SCI-06",  "Cell biology, genetics, evolution, and ecosystems."),
    ("Science", "7"):  ("Earth Science",             "SCI-07",  "Geology, meteorology, oceanography, and astronomy."),
    ("Science", "8"):  ("Physical Science",          "SCI-08",  "Motion, forces, energy, waves, and chemical reactions."),
    ("Science", "9"):  ("Biology",                   "SCI-09",  "Cell structure, heredity, evolution, and body systems."),
    ("Science", "10"): ("Chemistry",                 "SCI-10",  "Atomic structure, bonding, reactions, and stoichiometry."),
    ("Science", "11"): ("Physics",                   "SCI-11",  "Mechanics, electricity, magnetism, and waves."),
    ("Science", "12"): ("AP Environmental Science",  "SCI-12",  "Earth systems, biodiversity, pollution, and sustainability."),

    # --- HISTORY ---
    ("History", "KG"): ("Social Studies - K",        "HIST-KG", "Community helpers, maps, and family history."),
    ("History", "1"):  ("Social Studies - Grade 1",  "HIST-01", "Families, communities, and basic geography."),
    ("History", "2"):  ("Social Studies - Grade 2",  "HIST-02", "Local history, government, and cultural diversity."),
    ("History", "3"):  ("Social Studies - Grade 3",  "HIST-03", "State history, economics, and citizenship."),
    ("History", "4"):  ("Social Studies - Grade 4",  "HIST-04", "Regional geography, Native American history, and exploration."),
    ("History", "5"):  ("Social Studies - Grade 5",  "HIST-05", "U.S. history through the Civil War and Reconstruction."),
    ("History", "6"):  ("World History: Ancient",    "HIST-06", "Mesopotamia, Egypt, Greece, Rome, and ancient civilizations."),
    ("History", "7"):  ("World History: Medieval",   "HIST-07", "Middle Ages, Renaissance, Reformation, and early exploration."),
    ("History", "8"):  ("U.S. History",              "HIST-08", "American Revolution through Reconstruction."),
    ("History", "9"):  ("World History: Modern",     "HIST-09", "Industrialization, imperialism, World Wars, and Cold War."),
    ("History", "10"): ("U.S. History",              "HIST-10", "Progressivism through the present day."),
    ("History", "11"): ("AP U.S. History",           "HIST-11", "In-depth study of American history from colonization to present."),
    ("History", "12"): ("AP Government & Politics",  "HIST-12", "Constitutional principles, civil liberties, and political systems."),

    # --- ART ---
    ("Art", "KG"): ("Kindergarten Art",              "ART-KG",  "Color, shape, line, and basic studio techniques."),
    ("Art", "1"):  ("Grade 1 Art",                   "ART-01",  "Elements of art and introduction to various media."),
    ("Art", "2"):  ("Grade 2 Art",                   "ART-02",  "Principles of design and cultural art forms."),
    ("Art", "3"):  ("Grade 3 Art",                   "ART-03",  "Art history, mixed media, and creative expression."),
    ("Art", "4"):  ("Grade 4 Art",                   "ART-04",  "Drawing, painting, and sculpture fundamentals."),
    ("Art", "5"):  ("Grade 5 Art",                   "ART-05",  "Portfolio development and art critique."),
    ("Art", "6"):  ("Visual Arts 6",                 "ART-06",  "Drawing, painting, and introduction to digital art."),
    ("Art", "7"):  ("Visual Arts 7",                 "ART-07",  "Printmaking, ceramics, and art history connections."),
    ("Art", "8"):  ("Visual Arts 8",                 "ART-08",  "Mixed media, photography basics, and portfolio preparation."),
    ("Art", "9"):  ("Studio Art I",                  "ART-09",  "Foundational studio techniques across multiple media."),
    ("Art", "10"): ("Studio Art II",                 "ART-10",  "Advanced studio work and thematic project development."),
    ("Art", "11"): ("AP Studio Art: Drawing",        "ART-11",  "Portfolio-based course in drawing and compositional skills."),
    ("Art", "12"): ("AP Art History",                "ART-12",  "Global art history from prehistoric times to the present."),

    # --- PE ---
    ("PE", "KG"): ("Kindergarten PE",                "PE-KG",   "Gross motor skills, movement, and cooperative games."),
    ("PE", "1"):  ("Grade 1 PE",                     "PE-01",   "Locomotor skills, balance, and partner activities."),
    ("PE", "2"):  ("Grade 2 PE",                     "PE-02",   "Ball skills, fitness concepts, and team games."),
    ("PE", "3"):  ("Grade 3 PE",                     "PE-03",   "Cooperative games, fitness testing, and sportsmanship."),
    ("PE", "4"):  ("Grade 4 PE",                     "PE-04",   "Sport skills, health-related fitness, and goal setting."),
    ("PE", "5"):  ("Grade 5 PE",                     "PE-05",   "Team sports, individual fitness, and wellness education."),
    ("PE", "6"):  ("Physical Education 6",           "PE-06",   "Team sports, fitness assessment, and personal health goals."),
    ("PE", "7"):  ("Physical Education 7",           "PE-07",   "Lifetime fitness activities and sport-specific skills."),
    ("PE", "8"):  ("Physical Education 8",           "PE-08",   "Fitness planning, nutrition, and competitive sports."),
    ("PE", "9"):  ("Health & PE 9",                  "PE-09",   "Physical fitness, mental health, and consumer health."),
    ("PE", "10"): ("Health & PE 10",                 "PE-10",   "Team sports, personal fitness plans, and stress management."),
    ("PE", "11"): ("Fitness & Wellness",             "PE-11",   "Exercise science, nutrition, and lifelong wellness habits."),
    ("PE", "12"): ("Sports Medicine",                "PE-12",   "Athletic training, injury prevention, and rehabilitation basics."),

    # --- SUMMER ---
    ("Summer Math", "KG"): ("Summer Math - K",       "SUM-MATH-KG", "Summer enrichment in number sense and counting."),
    ("Summer Math", "1"):  ("Summer Math - Grade 1", "SUM-MATH-01", "Summer review of addition, subtraction, and place value."),
    ("Summer Math", "2"):  ("Summer Math - Grade 2", "SUM-MATH-02", "Summer review of multi-digit operations and measurement."),
    ("Summer Math", "3"):  ("Summer Math - Grade 3", "SUM-MATH-03", "Summer review of multiplication, division, and fractions."),
    ("Summer Math", "4"):  ("Summer Math - Grade 4", "SUM-MATH-04", "Summer review of fractions, decimals, and geometry."),
    ("Summer Math", "5"):  ("Summer Math - Grade 5", "SUM-MATH-05", "Summer review of fractions, decimals, and ratios."),
    ("Summer Math", "6"):  ("Summer Pre-Algebra",    "SUM-MATH-06", "Summer enrichment in ratios and early algebraic thinking."),
    ("Summer Math", "7"):  ("Summer Algebra 1",      "SUM-MATH-07", "Summer bridge course for algebra readiness."),
    ("Summer Math", "8"):  ("Summer Algebra 2",      "SUM-MATH-08", "Summer review of quadratic functions and polynomials."),
    ("Summer Math", "9"):  ("Summer Geometry",       "SUM-MATH-09", "Summer review of geometric proofs and trigonometry."),
    ("Summer Math", "10"): ("Summer Pre-Calculus",   "SUM-MATH-10", "Summer bridge to calculus concepts."),
    ("Summer Math", "11"): ("Summer Calculus",       "SUM-MATH-11", "Summer enrichment in differential calculus."),
    ("Summer Math", "12"): ("Summer Math Elective",  "SUM-MATH-12", "Advanced summer mathematics topics."),
    ("Summer Reading", "KG"): ("Summer Reading - K",       "SUM-ELA-KG",  "Summer phonics and early literacy enrichment."),
    ("Summer Reading", "1"):  ("Summer Reading - Grade 1", "SUM-ELA-01",  "Summer fluency and comprehension enrichment."),
    ("Summer Reading", "2"):  ("Summer Reading - Grade 2", "SUM-ELA-02",  "Summer vocabulary and reading comprehension."),
    ("Summer Reading", "3"):  ("Summer Reading - Grade 3", "SUM-ELA-03",  "Summer literature and writing enrichment."),
    ("Summer Reading", "4"):  ("Summer Reading - Grade 4", "SUM-ELA-04",  "Summer reading and essay writing enrichment."),
    ("Summer Reading", "5"):  ("Summer Reading - Grade 5", "SUM-ELA-05",  "Summer literary analysis and writing practice."),
    ("Summer Reading", "6"):  ("Summer English 6",         "SUM-ELA-06",  "Summer reading and composition enrichment."),
    ("Summer Reading", "7"):  ("Summer English 7",         "SUM-ELA-07",  "Summer literature and writing enrichment."),
    ("Summer Reading", "8"):  ("Summer English 8",         "SUM-ELA-08",  "Summer argumentative writing and reading practice."),
    ("Summer Reading", "9"):  ("Summer English 9",         "SUM-ELA-09",  "Summer world literature and writing enrichment."),
    ("Summer Reading", "10"): ("Summer English 10",        "SUM-ELA-10",  "Summer American literature and essay writing."),
    ("Summer Reading", "11"): ("Summer AP Language",       "SUM-ELA-11",  "Summer prep for AP Language and Composition."),
    ("Summer Reading", "12"): ("Summer AP Literature",     "SUM-ELA-12",  "Summer prep for AP Literature and Composition."),
    ("Summer Credit Recovery", "KG"): ("Summer Credit Recovery", "SUM-CR-KG", "Credit recovery and academic support program."),
    ("Summer Credit Recovery", "1"):  ("Summer Credit Recovery", "SUM-CR-01", "Credit recovery and academic support program."),
    ("Summer Credit Recovery", "2"):  ("Summer Credit Recovery", "SUM-CR-02", "Credit recovery and academic support program."),
    ("Summer Credit Recovery", "3"):  ("Summer Credit Recovery", "SUM-CR-03", "Credit recovery and academic support program."),
    ("Summer Credit Recovery", "4"):  ("Summer Credit Recovery", "SUM-CR-04", "Credit recovery and academic support program."),
    ("Summer Credit Recovery", "5"):  ("Summer Credit Recovery", "SUM-CR-05", "Credit recovery and academic support program."),
    ("Summer Credit Recovery", "6"):  ("Summer Credit Recovery", "SUM-CR-06", "Credit recovery and academic support program."),
    ("Summer Credit Recovery", "7"):  ("Summer Credit Recovery", "SUM-CR-07", "Credit recovery and academic support program."),
    ("Summer Credit Recovery", "8"):  ("Summer Credit Recovery", "SUM-CR-08", "Credit recovery and academic support program."),
    ("Summer Credit Recovery", "9"):  ("Summer Credit Recovery", "SUM-CR-09", "Credit recovery and academic support program."),
    ("Summer Credit Recovery", "10"): ("Summer Credit Recovery", "SUM-CR-10", "Credit recovery and academic support program."),
    ("Summer Credit Recovery", "11"): ("Summer Credit Recovery", "SUM-CR-11", "Credit recovery and academic support program."),
    ("Summer Credit Recovery", "12"): ("Summer Credit Recovery", "SUM-CR-12", "Credit recovery and academic support program."),
}

def get_course(subject, grade):
    """
    Look up course name, number, and description from the catalog.
    Falls back gracefully if the (subject, grade) combo isn't in the catalog.
    """
    entry = COURSE_CATALOG.get((subject, str(grade)))
    if entry:
        return entry[0], entry[1], entry[2]
    # Fallback: generic name for unmapped combos (e.g. edge case grades like '-1', '13')
    return f"{subject} - Grade {grade}", f"{subject[:3].upper()}-{str(grade).zfill(2)}", f"{subject} course for grade {grade}."

DISABILITY_MAP = {"AUT": "Autism", "SLD": "Specific learning disability", "SLI": "Speech or language impairment"}
DISABILITY_CODES = list(DISABILITY_MAP.keys())

# ==========================================
# 3. HELPER FUNCTIONS
# ==========================================
def get_hex_id(length=6, prefix=""):
    """
    Generate a random hex ID of the specified length with an optional prefix.
    Prefix prevents Excel from misinterpreting hex strings as scientific notation
    (e.g. bare '9e9554' → Excel renders as '9E+9554'). A letter prefix like 's-'
    ensures the value is always treated as a string regardless of its hex digits.
    ID space: 16^length (e.g. 6-char = 16,777,216 unique values per prefix).
    """
    return f"{prefix}{uuid.uuid4().hex[:length]}"

# Typed ID generators — each entity type gets its own prefix.
# This keeps IDs visually distinct, Excel-safe, and easy to identify at a glance.
def make_school_id(mode, base=0, counter=0):
    return f"sch-{uuid.uuid4().hex[:6]}" if mode == 'alphanumeric' else get_sequential_id(base, counter)

def make_teacher_id(mode, base=0, counter=0):
    return f"tch-{uuid.uuid4().hex[:7]}" if mode == 'alphanumeric' else get_sequential_id(base, counter)

def make_student_id(mode, base=0, counter=0):
    return f"stu-{uuid.uuid4().hex[:6]}" if mode == 'alphanumeric' else get_sequential_id(base, counter)

def make_section_id(mode):
    return f"sec-{uuid.uuid4().hex[:8]}" if mode == 'alphanumeric' else f"SEC-{uuid.uuid4().hex[:8]}"

def make_staff_id(mode, base=0, counter=0):
    return f"stf-{uuid.uuid4().hex[:7]}" if mode == 'alphanumeric' else get_sequential_id(base, counter)

def get_sequential_id(base, counter):
    return str(base + counter)

def clean_phone():
    digits = re.sub("[^0-9]", "", fake.phone_number())
    if len(digits) < 10: digits = digits.ljust(10, '0')
    return f"{digits[:3]}-{digits[3:6]}-{digits[6:10]}"

def parse_count(val_input):
    val_str = str(val_input).strip()
    if "-" in val_str:
        try:
            low, high = map(int, val_str.split("-"))
            return max(1, random.randint(low, high))
        except: return 10
    else:
        try: return max(1, int(val_str))
        except: return 10

def generate_dob(grade):
    current_year = datetime.date.today().year
    grade_map = {'PK': 4, 'KG': 5, '1': 6, '2': 7, '3': 8, '4': 9, '5': 10, '6': 11, '7': 12, '8': 13, '9': 14, '10': 15, '11': 16, '12': 17}
    return fake.date_between(start_date=datetime.date(current_year - grade_map.get(grade, 10), 1, 1), end_date=datetime.date(current_year - grade_map.get(grade, 10), 12, 31)).strftime('%Y-%m-%d')

def generate_email_username(first, last, domain, fmt):
    f, l = re.sub(r'[^a-z]', '', first.lower()), re.sub(r'[^a-z]', '', last.lower())
    u = f"{f}.{l}{random.randint(10, 99)}"
    return u, f"{u}@{domain}"

def generate_term_schedule(anchor_year_str, num_terms):
    y_start = int(anchor_year_str)
    y_end = y_start + 1
    terms = []
    if num_terms == 2:
        terms.append({"Term_name": f"Sem 1 {y_start}", "Term_start": f"{y_start}-08-15", "Term_end": f"{y_start}-12-20"})
        terms.append({"Term_name": f"Sem 2 {y_end}", "Term_start": f"{y_end}-01-05", "Term_end": f"{y_end}-05-25"})
    return terms

def generate_summer_term(anchor_year_str):
    y_end = int(anchor_year_str) + 1
    return {"Term_name": f"Summer {y_end}", "Term_start": f"{y_end}-06-01", "Term_end": f"{y_end}-07-30"}

def generate_household_contacts(student_last_name):
    rel_options = [("Mother", "female", "Parent/Guardian"), ("Father", "male", "Parent/Guardian"), ("Grandmother", "female", "Emergency"), ("Grandfather", "male", "Emergency"), ("Aunt", "female", "Emergency"), ("Uncle", "male", "Emergency"), ("Guardian", "neutral", "Parent/Guardian")]
    choice = random.choices(rel_options, weights=[40, 40, 5, 5, 3, 3, 4], k=1)[0]
    relationship, gender, contact_type = choice
    f_name = census_first_name("F") if gender == "female" else census_first_name("M") if gender == "male" else census_first_name()
    return [{
        "Contact_relationship": relationship,
        "Contact_type": contact_type,
        "Contact_name": f"{f_name} {student_last_name}",
        "Contact_phone": clean_phone(),
        "Contact_phone_type": "Cell",
        "Contact_email": f"{re.sub(r'[^a-z]', '', f_name.lower())}.{re.sub(r'[^a-z]', '', student_last_name.lower())}@example.com",
        "Contact_sis_id": f"cont-{uuid.uuid4().hex[:8]}"
    }]

# --- FILE STREAMING HELPERS ---
def init_files(out_dir, schema, do_attendance=False, do_resources=False):
    HEADERS = {
        "schools": ["School_id", "School_name", "School_number", "Low_grade", "High_grade", "Principal", "Principal_email", "School_address", "School_city", "School_state", "School_zip", "School_phone"],
        "teachers": ["School_id", "Teacher_id", "Teacher_number", "State_teacher_id", "Teacher_email", "Username", "First_name", "Last_name", "Title"],
        "staff": ["School_id", "Staff_id", "Staff_email", "First_name", "Last_name", "Department", "Title"],
        "students": ["School_id", "Student_id", "Student_number", "State_id", "Last_name", "First_name", "Grade", "Gender", "DOB", "Student_email", "Username", "Race", "Hispanic_latino", "Home_language", "IEP_status", "FRL_status", "ELL_status", "Section_504_status", "Gifted_status", "Disability_status", "Disability_type", "Disability_code", "ext.locker_number", "ext.bus_route", "Contact_relationship", "Contact_type", "Contact_name", "Contact_phone", "Contact_phone_type", "Contact_email", "Contact_sis_id"],
        "sections": ["School_id", "Section_id", "Teacher_id", "Teacher_2_id", "Name", "Course_name", "Course_number", "Course_description", "Grade", "Subject", "Term_name", "Term_start", "Term_end", "Period"],
        "enrollments": ["School_id", "Section_id", "Student_id"],
        "attendance": ["Attendance_id", "School_id", "Student_id", "Section_id", "Attendance_date", "Attendance_status", "Attendance_type", "Excuse_code"],
        "resources": ["Resource_id", "Title", "Roles", "Course_number", "Course_name"],
        "users": ["School_name", "User_type", "User_id", "First_name", "Last_name", "Email", "Username", "Grade", "DOB"],
        "anyschool_sections": ["School_name", "Section_id", "User_id", "Teacher_id", "School_number", "Subject", "Period", "Section_name"]
    }
    paths = {}
    if schema in ["standard", "both"]:
        std_dir = os.path.join(out_dir, "standard")
        os.makedirs(std_dir, exist_ok=True)
        for k in ["schools", "teachers", "staff", "students", "sections", "enrollments"]:
            p = os.path.join(std_dir, f"{k}.csv")
            pd.DataFrame(columns=HEADERS[k]).to_csv(p, index=False)
            paths[f"std_{k}"] = p
        if do_attendance:
            p = os.path.join(std_dir, "attendance.csv")
            pd.DataFrame(columns=HEADERS["attendance"]).to_csv(p, index=False)
            paths["std_attendance"] = p
        if do_resources:
            p = os.path.join(std_dir, "resources.csv")
            pd.DataFrame(columns=HEADERS["resources"]).to_csv(p, index=False)
            paths["std_resources"] = p

    if schema in ["anyschool", "both"]:
        as_dir = os.path.join(out_dir, "anyschool")
        os.makedirs(as_dir, exist_ok=True)
        paths["as_users"] = os.path.join(as_dir, "users.csv")
        paths["as_sections"] = os.path.join(as_dir, "sections.csv")
        pd.DataFrame(columns=HEADERS["users"]).to_csv(paths["as_users"], index=False)
        pd.DataFrame(columns=HEADERS["anyschool_sections"]).to_csv(paths["as_sections"], index=False)
    return paths

def append_data(data, filepath):
    if data: pd.DataFrame(data).to_csv(filepath, mode='a', header=False, index=False)

def transform_to_anyschool(students, teachers, staff, sections, enrollments, schools):
    school_map = {s['School_id']: {'name': s['School_name'], 'number': s['School_number']} for s in schools}
    def fmt_date(d):
        try: return datetime.datetime.strptime(d, "%Y-%m-%d").strftime("%m/%d/%Y")
        except: return d

    GRADE_MAP = {"KG": "Kindergarten", "PK": "PreKindergarten"}
    SUBJECT_MAP = {"Math": "math", "Science": "science", "ELA": "english/language arts", "History": "social studies", "Art": "arts and music", "PE": "pe and health", "Summer Math": "math", "Summer Reading": "english/language arts", "Summer Credit Recovery": "other"}

    users_out, sections_out = [], []
    seen_students = set()
    for s in students:
        if s['Student_id'] in seen_students: continue
        seen_students.add(s['Student_id'])
        users_out.append({
            "School_name": school_map[s['School_id']]['name'],
            "User_type": "student",
            "User_id": s['Student_id'],
            "First_name": s['First_name'],
            "Last_name": s['Last_name'],
            "Email": s['Student_email'],
            "Username": s.get('Username', ''),
            "Grade": GRADE_MAP.get(str(s['Grade']), str(s['Grade'])),
            "DOB": fmt_date(s['DOB'])
        })

    for t in teachers: users_out.append({"School_name": school_map[t['School_id']]['name'], "User_type": "teacher", "User_id": t['Teacher_id'], "First_name": t['First_name'], "Last_name": t['Last_name'], "Email": t['Teacher_email'], "Username": t.get('Username', ''), "Grade": "", "DOB": ""})
    for st in staff: users_out.append({"School_name": school_map[st['School_id']]['name'], "User_type": "staff", "User_id": st['Staff_id'], "First_name": st['First_name'], "Last_name": st['Last_name'], "Email": st['Staff_email'], "Username": st.get('Staff_email', '').split('@')[0], "Grade": "", "DOB": ""})

    sec_lookup = {x['Section_id']: x for x in sections}
    for e in enrollments:
        sd = sec_lookup.get(e['Section_id'])
        if sd:
            sections_out.append({
                "School_name": school_map[e['School_id']]['name'],
                "Section_id": e['Section_id'],
                "User_id": e['Student_id'],
                "Teacher_id": sd['Teacher_id'],
                "School_number": school_map[e['School_id']]['number'],
                "Subject": SUBJECT_MAP.get(sd['Subject'], "other"),
                "Period": sd.get('Period', "1"),
                "Section_name": sd['Name']
            })
    return users_out, sections_out

def export_district_state(config, base_dir, dist_name, folder_suffix, db):
    out_dir = os.path.join(base_dir, f"{dist_name}_{folder_suffix}")
    os.makedirs(out_dir, exist_ok=True)
    file_paths = init_files(out_dir, config["OUTPUT_SCHEMA"], do_attendance=config.get("DO_ATTENDANCE", False), do_resources=config.get("DO_RESOURCES", False))
    if "std_schools" in file_paths:
        for data, key in [(db["schools"], "std_schools"), (db["teachers"], "std_teachers"), (db["staff"], "std_staff"), (db["students"], "std_students"), (db["sections"], "std_sections"), (db["enrollments"], "std_enrollments")]:
            append_data(data, file_paths[key])
        if config.get("DO_ATTENDANCE", False) and "std_attendance" in file_paths:
            append_data(db["attendance"], file_paths["std_attendance"])
        if config.get("DO_RESOURCES", False) and "std_resources" in file_paths:
            append_data(db["resources"], file_paths["std_resources"])
    if "as_users" in file_paths:
        u_chunk, s_chunk = transform_to_anyschool(db["students"], db["teachers"], db["staff"], db["sections"], db["enrollments"], db["schools"])
        append_data(u_chunk, file_paths["as_users"])
        append_data(s_chunk, file_paths["as_sections"])

# ==========================================
# 4. MAIN GENERATION ENGINE
# ==========================================
def run_generation(config, base_output_dir, status_callback=None, progress_callback=None):
    random.shuffle(GENERIC_DISTRICT_NAMES)
    CORE_TERMS = generate_term_schedule(config["SCHOOL_START_YEAR"], config["NUM_TERMS"])

    active_cases, do_3_day = get_active_cases(config)

    # --- EDGE CASE REPORT (keyed by new scenario labels) ---
    edge_case_report = {f"Scenario {ec['number']} ({ec['label']})": [] for ec in EDGE_CASE_REGISTRY}

    def ec_report(key, msg):
        ec = EC_BY_KEY.get(key)
        if ec:
            edge_case_report[f"Scenario {ec['number']} ({ec['label']})"].append(msg)

    def ec_active(key):
        return key in active_cases

    for i in range(config["NUM_DISTRICTS"]):
        dist_name = GENERIC_DISTRICT_NAMES[i % len(GENERIC_DISTRICT_NAMES)]
        if status_callback: status_callback(f"Generating {dist_name}...")
        current_domain = config["EMAIL_DOMAIN"] if config["EMAIL_DOMAIN"] else f"{dist_name.lower()}.k12.edu"
        state_abbr = STATE_MAPPINGS[STATE_KEYS[i % len(STATE_KEYS)]][1]
        base_id_seq = (i + 1) * 100000

        dist_db = {"schools": [], "teachers": [], "staff": [], "students": [], "sections": [], "enrollments": [], "attendance": [], "resources": []}
        _seen_student_ids = set()
        _seen_section_ids = set()

        school_type_sequence = get_school_type_sequence(config["SCHOOLS_PER_DISTRICT"])
        _seen_student_ids = set()   # collision guard — scoped per district
        _seen_section_ids = set()   # collision guard — scoped per district

        for s_idx in range(config["SCHOOLS_PER_DISTRICT"]):
            school_id = make_school_id(config["ID_MODE"], base_id_seq, s_idx * 10000)
            school_type = school_type_sequence[s_idx]
            low, high = ('KG', '5') if 'Elementary' in school_type else ('6', '8') if 'Middle' in school_type else ('9', '12') if 'High' in school_type else ('KG', '12')

            prin_first, prin_last = census_full_name()
            dist_db["schools"].append({"School_id": school_id, "School_name": f"{census_last_name()} {school_type}", "School_number": f"{s_idx + 1:02d}", "Low_grade": low, "High_grade": high, "Principal": f"{prin_first} {prin_last}", "Principal_email": f"principal.{school_id}@{current_domain}", "School_address": fake.street_address(), "School_city": random.choice(REAL_LOCATIONS.get(state_abbr, [("City", "000")]))[0], "School_state": state_abbr, "School_zip": f"900{random.randint(10, 99)}", "School_phone": fake.phone_number()})
            dist_db["staff"].append({"School_id": school_id, "Staff_id": make_staff_id(config["ID_MODE"], base_id_seq, 90000 + s_idx), "Staff_email": f"principal.{school_id}@{current_domain}", "First_name": prin_first, "Last_name": prin_last, "Department": "Administration", "Title": "Principal"})

            num_teachers = parse_count(config["TEACHERS_PER_SCHOOL"])
            school_teacher_ids = []
            for t_idx in range(num_teachers):
                t_id = make_teacher_id(config["ID_MODE"], base_id_seq, (s_idx * 1000) + t_idx)
                _tf, _tl = census_full_name()
                uname, email = generate_email_username(_tf, _tl, current_domain, config["USERNAME_FMT"])
                dist_db["teachers"].append({"School_id": school_id, "Teacher_id": t_id, "Teacher_number": t_id[:8], "State_teacher_id": f"{state_abbr}-{t_id[:8]}", "Teacher_email": email, "Username": uname, "First_name": _tf, "Last_name": _tl, "Title": "Teacher"})
                school_teacher_ids.append(t_id)

            # Sc 18: Teacher without Sections — pop one teacher before section assignment
            if ec_active("sc_18") and len(school_teacher_ids) > 2 and s_idx == 0:
                scen_18_teacher = school_teacher_ids.pop()
                ec_report("sc_18", f"Teacher_id: {scen_18_teacher}")

            grade_list = [str(g) if g > 0 else 'KG' for g in range(int(low) if low.isdigit() else 0, (int(high) if high.isdigit() else 12) + 1)]
            school_section_ids = []
            for t_id in school_teacher_ids:
                for term in CORE_TERMS:
                    t_start, t_end = term["Term_start"], term["Term_end"]
                    for period_idx in range(config["SECTIONS_PER_TEACHER_TERM"]):
                        sec_id = make_section_id(config["ID_MODE"])
                        while sec_id in _seen_section_ids:
                            sec_id = make_section_id(config["ID_MODE"])
                        _seen_section_ids.add(sec_id)
                        s_grade, s_subj = random.choice(grade_list), random.choice(['Math', 'Science', 'ELA', 'History', 'Art', 'PE'])
                        sec_name = f"{s_grade} - {s_subj}"
                        assigned_teacher = t_id

                        # Section-level probabilistic edge cases
                        r_sec = random.random()
                        if ec_active("sc_04") and r_sec < 0.02:
                            sec_name = str(random.randint(100000, 999999))
                            ec_report("sc_04", f"Section_id: {sec_id} (Name: {sec_name})")
                        elif ec_active("sc_05") and r_sec < 0.05:
                            sec_name = "Homeroom"
                            ec_report("sc_05", f"Section_id: {sec_id} (Name: {sec_name})")
                        elif ec_active("sc_19") and r_sec < 0.06:
                            sec_id = "".join([uuid.uuid4().hex for _ in range(3)])[:90]
                            ec_report("sc_19", f"Section_id: {sec_id}")
                        elif ec_active("sc_21") and r_sec < 0.07:
                            s_grade = "13"
                            ec_report("sc_21", f"Section_id: {sec_id} (Grade: 13)")
                        elif ec_active("sc_22") and r_sec < 0.08:
                            s_grade = "PK"
                            ec_report("sc_22", f"Section_id: {sec_id} (Subject: {s_subj}, Classified as PK)")
                        elif ec_active("sc_32") and r_sec < 0.09:
                            t_start, t_end = "2035-08-01", "2035-12-15"
                            ec_report("sc_32", f"Section_id: {sec_id} (Start: {t_start})")
                        elif ec_active("sc_06") and r_sec > 0.98:
                            assigned_teacher = ""
                            ec_report("sc_06", f"Section_id: {sec_id}")

                        _cname, _cnum, _cdesc = get_course(s_subj, s_grade)
                        dist_db["sections"].append({"School_id": school_id, "Section_id": sec_id, "Teacher_id": assigned_teacher, "Teacher_2_id": "", "Name": sec_name, "Course_name": _cname, "Course_number": _cnum, "Course_description": _cdesc, "Grade": s_grade, "Subject": s_subj, "Term_name": term["Term_name"], "Term_start": t_start, "Term_end": t_end, "Period": str(period_idx + 1)})
                        school_section_ids.append({"id": sec_id, "grade": s_grade})

            estimated_students = int((len(school_section_ids) * parse_count(config["STUDENTS_PER_SECTION"])) / config["SECTIONS_PER_TEACHER_TERM"])
            school_student_objs = []
            for stu_idx in range(estimated_students):
                stu_id = make_student_id(config["ID_MODE"], base_id_seq, 200000 + (s_idx * 5000) + stu_idx)
                while stu_id in _seen_student_ids:
                    stu_id = make_student_id(config["ID_MODE"])
                _seen_student_ids.add(stu_id)
                f, l, s_grade = census_first_name(), census_last_name(), random.choice(grade_list)

                # Student name / id edge cases
                r_val = random.random()
                if ec_active("sc_10") and r_val < 0.02:
                    l = "O'Connor"
                    ec_report("sc_10", f"Student_id: {stu_id}")
                elif ec_active("sc_10") and r_val < 0.04:
                    l = "Nuñez"
                    ec_report("sc_10", f"Student_id: {stu_id}")
                elif ec_active("sc_12") and r_val < 0.06:
                    l = "Li"
                    ec_report("sc_12", f"Student_id: {stu_id}")
                elif ec_active("sc_11") and r_val < 0.08:
                    l = "Wolfeschlegelsteinhausenbergerdorff" * 2
                    ec_report("sc_11", f"Student_id: {stu_id}")
                elif ec_active("sc_26") and r_val < 0.09:
                    s_grade = "-1"
                    ec_report("sc_26", f"Student_id: {stu_id} (Grade: -1)")
                elif ec_active("sc_29") and r_val < 0.10 and school_teacher_ids:
                    stu_id = school_teacher_ids[0]
                    ec_report("sc_29", f"Matched ID: {stu_id}")

                uname, email = generate_email_username(f, l, current_domain, config["USERNAME_FMT"])

                # Email edge cases
                if ec_active("sc_09") and random.random() < 0.02:
                    email = email.replace("@", "")
                    ec_report("sc_09", f"Student_id: {stu_id}")
                elif ec_active("sc_08") and random.random() < 0.02:
                    email = f"o'brien.{random.randint(10, 99)}@{current_domain}"
                    ec_report("sc_08", f"Student_id: {stu_id}")

                # Username edge cases
                if ec_active("sc_28") and random.random() < 0.03:
                    uname = ""
                    ec_report("sc_28", f"Student_id: {stu_id}")
                elif ec_active("sc_24") and random.random() < 0.02:
                    uname = uname + "superlongusername" * 3
                    ec_report("sc_24", f"Student_id: {stu_id}")

                dis_code = random.choice(DISABILITY_CODES) if random.random() < config["PROB_DISABILITY"] else ""

                # --- Correlated demographics: Hispanic_latino → Home_language → ELL_status ---
                # Step 1: Determine Hispanic/Latino identity from the slider value
                is_hispanic = random.random() < config["PROB_HISPANIC"]
                hispanic_val = "Y" if is_hispanic else "N"

                # Step 2: Derive Home_language weights from PROB_HISPANIC, then sample
                lang_weights = get_lang_weights(config["PROB_HISPANIC"])
                home_lang = random.choices(LANG_KEYS, weights=lang_weights)[0]
                is_spanish = home_lang == "spa"

                # Step 3: Derive ELL_status from the probability matrix
                ell_prob = ELL_PROB_MATRIX[(is_spanish, is_hispanic)]
                ell_val = "Y" if random.random() < ell_prob else "N"

                stu_obj = {
                    "School_id": school_id, "Student_id": stu_id, "Student_number": stu_id[:8], "State_id": f"{state_abbr}-{stu_id[:8]}",
                    "Last_name": l, "First_name": f, "Grade": s_grade, "Gender": random.choice(['M', 'F']),
                    "DOB": generate_dob(s_grade), "Student_email": email, "Username": uname,
                    "Race": random.choices(CLEVER_RACE_VALUES, weights=RACE_WEIGHTS)[0],
                    "Hispanic_latino": hispanic_val,
                    "Home_language": home_lang,
                    "IEP_status": "Y" if random.random() < config["PROB_IEP"] else "N",
                    "FRL_status": "Y" if random.random() < config["PROB_FRL"] else "N",
                    "ELL_status": ell_val,
                    "Section_504_status": "Y" if random.random() < config["PROB_504"] else "N",
                    "Gifted_status": "Y" if random.random() < config["PROB_GIFTED"] else "N",
                    "Disability_status": "Y" if dis_code else "N",
                    "Disability_type": DISABILITY_MAP.get(dis_code, ""),
                    "Disability_code": dis_code,
                    "ext.locker_number": "", "ext.bus_route": "",
                    "Contact_relationship": "", "Contact_type": "", "Contact_name": "",
                    "Contact_phone": "", "Contact_phone_type": "", "Contact_email": "", "Contact_sis_id": ""
                }
                school_student_objs.append(stu_obj)
                if config["DO_CONTACTS"]:
                    for c in generate_household_contacts(l):
                        r = stu_obj.copy(); r.update(c); dist_db["students"].append(r)
                else:
                    dist_db["students"].append(stu_obj)

            students_by_grade = {g: [s for s in school_student_objs if s['Grade'] == g] for g in grade_list}
            for sec in school_section_ids:
                avail = students_by_grade.get(sec['grade'], [])
                if avail:
                    for s in random.sample(avail, k=min(parse_count(config["STUDENTS_PER_SECTION"]), len(avail))):
                        dist_db["enrollments"].append({"School_id": school_id, "Section_id": sec['id'], "Student_id": s['Student_id']})


            # --- RESOURCE GENERATION ---
            # Generate 1-3 synthetic resources per unique course taught in this school.
            # Resources link to courses via Course_number, matching the Clever content
            # mapping model (resources → courses → sections).
            if config.get("DO_RESOURCES", False):
                seen_courses = {}
                for sec in dist_db["sections"]:
                    if sec["School_id"] != school_id: continue
                    key = sec["Course_number"]
                    if key not in seen_courses:
                        seen_courses[key] = (sec["Course_name"], sec["Course_number"])
                for course_num, (course_name, course_number) in seen_courses.items():
                    num_resources = random.randint(1, 3)
                    for r_idx in range(num_resources):
                        resource_types = [
                            ("Lesson", "student"),
                            ("Quiz", "student"),
                            ("Assessment", "teacher,student"),
                            ("Assignment", "student"),
                            ("Teacher Guide", "teacher"),
                            ("Practice Set", "student"),
                            ("Unit Overview", "teacher"),
                            ("Video", "student"),
                            ("Reading", "student"),
                            ("Worksheet", "student"),
                        ]
                        r_type, r_roles = random.choice(resource_types)
                        r_title = f"{course_name} - {r_type} {r_idx + 1}"
                        r_id = f"res-{uuid.uuid4().hex[:8]}"
                        dist_db["resources"].append({
                            "Resource_id": r_id,
                            "Title": r_title,
                            "Roles": r_roles,
                            "Course_number": course_number,
                            "Course_name": course_name,
                        })

            # Sc 35: Teacher with No Student Mapping
            # Done once (first school only): add a real teacher whose sections get zero enrollments.
            if ec_active("sc_35") and s_idx == 0:
                sc35_t_id = make_teacher_id(config["ID_MODE"], base_id_seq, 88801)
                _sc35f, _sc35l = census_full_name()
                sc35_uname, sc35_email = generate_email_username(_sc35f, _sc35l, current_domain, config["USERNAME_FMT"])
                dist_db["teachers"].append({"School_id": school_id, "Teacher_id": sc35_t_id, "Teacher_number": sc35_t_id[:8], "State_teacher_id": f"{state_abbr}-{sc35_t_id[:8]}", "Teacher_email": sc35_email, "Username": sc35_uname, "First_name": _sc35f, "Last_name": _sc35l, "Title": "Teacher"})
                for p_idx in range(config["SECTIONS_PER_TEACHER_TERM"]):
                    sc35_sec_id = make_section_id(config["ID_MODE"])
                    s_grade = random.choice(grade_list)
                    _sc35_cname, _sc35_cnum, _sc35_cdesc = get_course("Math", s_grade)
                    dist_db["sections"].append({"School_id": school_id, "Section_id": sc35_sec_id, "Teacher_id": sc35_t_id, "Teacher_2_id": "", "Name": f"{s_grade} - Math", "Course_name": _sc35_cname, "Course_number": _sc35_cnum, "Course_description": _sc35_cdesc, "Grade": s_grade, "Subject": "Math", "Term_name": CORE_TERMS[0]["Term_name"], "Term_start": CORE_TERMS[0]["Term_start"], "Term_end": CORE_TERMS[0]["Term_end"], "Period": str(p_idx + 1)})
                    # Intentionally no enrollments added for these sections
                ec_report("sc_35", f"Teacher_id: {sc35_t_id} (school: {school_id}, {config['SECTIONS_PER_TEACHER_TERM']} sections, 0 enrollments)")

            # Sc 36: Student Mapped to Only One Teacher
            # Done once (first school only): create one student and enroll them only in sections
            # belonging to a single teacher.
            if ec_active("sc_36") and s_idx == 0 and school_teacher_ids:
                sc36_teacher_id = school_teacher_ids[0]
                sc36_teacher_sections = [sec for sec in dist_db["sections"] if sec["Teacher_id"] == sc36_teacher_id and sec["School_id"] == school_id]
                if sc36_teacher_sections:
                    sc36_stu_id = make_student_id(config["ID_MODE"], base_id_seq, 88802)
                    sc36_f, sc36_l = census_full_name()
                    sc36_uname, sc36_email = generate_email_username(sc36_f, sc36_l, current_domain, config["USERNAME_FMT"])
                    sc36_grade = sc36_teacher_sections[0]["Grade"] if sc36_teacher_sections[0]["Grade"] in grade_list else grade_list[0]
                    sc36_stu = {"School_id": school_id, "Student_id": sc36_stu_id, "Student_number": sc36_stu_id[:8], "State_id": f"{state_abbr}-{sc36_stu_id[:8]}", "Last_name": sc36_l, "First_name": sc36_f, "Grade": sc36_grade, "Gender": random.choice(['M', 'F']), "DOB": generate_dob(sc36_grade), "Student_email": sc36_email, "Username": sc36_uname, "Race": random.choices(CLEVER_RACE_VALUES, weights=RACE_WEIGHTS)[0], "Hispanic_latino": "N", "Home_language": random.choices(LANG_KEYS, weights=get_lang_weights(config["PROB_HISPANIC"]))[0], "IEP_status": "N", "FRL_status": "N", "ELL_status": "N", "Section_504_status": "N", "Gifted_status": "N", "Disability_status": "N", "Disability_type": "", "Disability_code": "", "ext.locker_number": "", "ext.bus_route": "", "Contact_relationship": "", "Contact_type": "", "Contact_name": "", "Contact_phone": "", "Contact_phone_type": "", "Contact_email": "", "Contact_sis_id": ""}
                    dist_db["students"].append(sc36_stu)
                    # Enroll only in this one teacher's sections
                    for sec in sc36_teacher_sections:
                        dist_db["enrollments"].append({"School_id": school_id, "Section_id": sec["Section_id"], "Student_id": sc36_stu_id})
                    ec_report("sc_36", f"Student_id: {sc36_stu_id} enrolled only in sections of Teacher_id: {sc36_teacher_id} ({len(sc36_teacher_sections)} sections)")

            if s_idx == 0:
                dist_db["staff"].insert(0, {"School_id": school_id, "Staff_id": make_staff_id(config["ID_MODE"], base_id_seq, 99999), "Staff_email": f"admin@{current_domain}", "First_name": "System", "Last_name": "Admin", "Department": "Central", "Title": "Admin"})

        # --- MULTI-SCHOOL STATIC EDGE CASES ---
        if len(dist_db["schools"]) > 1:
            school_a, school_b = dist_db["schools"][0]["School_id"], dist_db["schools"][1]["School_id"]

            if ec_active("sc_01"):
                scen_01_teacher = next((t for t in dist_db["teachers"] if t["School_id"] == school_a), None)
                if scen_01_teacher:
                    t_copy = scen_01_teacher.copy(); t_copy["School_id"] = school_b; dist_db["teachers"].append(t_copy)
                    ec_report("sc_01", f"Teacher_id: {t_copy['Teacher_id']}")

            scen_02_student = None
            if ec_active("sc_02"):
                scen_02_student = next((s for s in dist_db["students"] if s["School_id"] == school_a), None)
                if scen_02_student:
                    s_copy = scen_02_student.copy(); s_copy["School_id"] = school_b; dist_db["students"].append(s_copy)
                    ec_report("sc_02", f"Student_id: {s_copy['Student_id']}")

            if ec_active("sc_03"):
                scen_03_staff = next((st for st in dist_db["staff"] if st["School_id"] == school_a and st["Title"] != "Admin"), None)
                if scen_03_staff:
                    st_copy = scen_03_staff.copy(); st_copy["School_id"] = school_b; dist_db["staff"].append(st_copy)
                    ec_report("sc_03", f"Staff_id: {st_copy['Staff_id']}")

            scen_13_section = next((sec for sec in dist_db["sections"] if sec["School_id"] == school_b), None)
            if ec_active("sc_13"):
                exclude_id = scen_02_student.get("Student_id") if scen_02_student else None
                scen_13_student = next((s for s in dist_db["students"] if s["School_id"] == school_a and s["Student_id"] != exclude_id), None)
                if scen_13_student and scen_13_section:
                    dist_db["enrollments"].append({"School_id": school_b, "Section_id": scen_13_section["Section_id"], "Student_id": scen_13_student["Student_id"]})
                    ec_report("sc_13", f"Student_id: {scen_13_student['Student_id']} into Section: {scen_13_section['Section_id']}")

            if ec_active("sc_14"):
                sc01_teacher_id = next((t["Teacher_id"] for t in dist_db["teachers"] if t["School_id"] == school_a), None)
                scen_14_teacher = next((t for t in dist_db["teachers"] if t["School_id"] == school_a and t["Teacher_id"] != sc01_teacher_id), None)
                scen_14_section = next((sec for sec in dist_db["sections"] if sec["School_id"] == school_b and (scen_13_section is None or sec["Section_id"] != scen_13_section["Section_id"])), None)
                if scen_14_teacher and scen_14_section:
                    scen_14_section["Teacher_id"] = scen_14_teacher["Teacher_id"]
                    ec_report("sc_14", f"Teacher_id: {scen_14_teacher['Teacher_id']} into Section: {scen_14_section['Section_id']}")

            if ec_active("sc_23"):
                scen_23_school = dist_db["schools"][-1]
                split_school_id = make_school_id(config["ID_MODE"], base_id_seq, 99999)
                split_school = scen_23_school.copy(); split_school["School_id"] = split_school_id; split_school["School_name"] = scen_23_school["School_name"] + " - Annex"
                dist_db["schools"].append(split_school)
                ec_report("sc_23", f"Split Annex: {split_school_id}")

            # Sc 37: Teachers Spanning Same and Different Schools
            # Duplicate 2 teachers from school_a into school_b so the dataset contains both
            # single-school teachers (the majority) and multi-school teachers (these two).
            if ec_active("sc_37"):
                sc37_candidates = [t for t in dist_db["teachers"] if t["School_id"] == school_a][:2]
                for t in sc37_candidates:
                    t_copy = t.copy(); t_copy["School_id"] = school_b
                    dist_db["teachers"].append(t_copy)
                    ec_report("sc_37", f"Teacher_id: {t_copy['Teacher_id']} duplicated into school {school_b} (also in {school_a})")

        # Sc 38: Section with Large Enrollment (50+ students)
        # Pick one existing section and force-enroll 50 students from the same school into it.
        if ec_active("sc_38") and dist_db["sections"] and dist_db["students"]:
            sc38_section = dist_db["sections"][0]
            sc38_school_id = sc38_section["School_id"]
            sc38_pool = [s for s in dist_db["students"] if s["School_id"] == sc38_school_id]
            sc38_targets = random.sample(sc38_pool, k=min(50, len(sc38_pool)))
            existing_enrolled = {e["Student_id"] for e in dist_db["enrollments"] if e["Section_id"] == sc38_section["Section_id"]}
            added = 0
            for s in sc38_targets:
                if s["Student_id"] not in existing_enrolled:
                    dist_db["enrollments"].append({"School_id": sc38_school_id, "Section_id": sc38_section["Section_id"], "Student_id": s["Student_id"]})
                    added += 1
            final_count = len([e for e in dist_db["enrollments"] if e["Section_id"] == sc38_section["Section_id"]])
            ec_report("sc_38", f"Section_id: {sc38_section['Section_id']} inflated to {final_count} enrollments")

        # Sc 39: Section with Minimal Enrollment (1-2 students)
        # Pick one section that has normal enrollments and strip it down to 1-2 students.
        if ec_active("sc_39") and dist_db["sections"]:
            sc39_section = dist_db["sections"][1] if len(dist_db["sections"]) > 1 else dist_db["sections"][0]
            sc39_sec_id = sc39_section["Section_id"]
            sc39_enrolled = [e for e in dist_db["enrollments"] if e["Section_id"] == sc39_sec_id]
            keep_count = random.randint(1, 2)
            keep = sc39_enrolled[:keep_count]
            dist_db["enrollments"] = [e for e in dist_db["enrollments"] if e["Section_id"] != sc39_sec_id] + keep
            ec_report("sc_39", f"Section_id: {sc39_sec_id} reduced to {len(keep)} enrollment(s)")

        if ec_active("sc_17") and dist_db["enrollments"] and dist_db["students"]:
            scen_17_student = dist_db["students"][0]["Student_id"]
            dist_db["enrollments"] = [e for e in dist_db["enrollments"] if e["Student_id"] != scen_17_student]
            ec_report("sc_17", f"Student_id: {scen_17_student}")

        if ec_active("sc_25") and len(dist_db["students"]) > 1 and dist_db["sections"]:
            scen_25_student = dist_db["students"][-1]
            scen_25_section = dist_db["sections"][0]
            dist_db["enrollments"].append({"School_id": scen_25_section["School_id"], "Section_id": scen_25_section["Section_id"], "Student_id": scen_25_student["Student_id"]})
            ec_report("sc_25", f"Student: {scen_25_student['Student_id']} forced into Section: {scen_25_section['Section_id']}")

        # --- 3-DAY ROTATION ENGINE ---
        if not do_3_day:
            export_district_state(config, base_output_dir, dist_name, "Data", dist_db)
        else:
            export_district_state(config, base_output_dir, dist_name, "Day_1", dist_db)

            # Day 2 mutations
            if ec_active("sc_15"):
                mia_student = dist_db["students"].pop(random.randint(0, len(dist_db["students"]) - 1))
                mia_student_enrollments = [e for e in dist_db["enrollments"] if e["Student_id"] == mia_student["Student_id"]]
                dist_db["enrollments"] = [e for e in dist_db["enrollments"] if e["Student_id"] != mia_student["Student_id"]]
                ec_report("sc_15", f"Student_id: {mia_student['Student_id']}")
            else:
                mia_student = None
                mia_student_enrollments = []

            if ec_active("sc_16"):
                mia_section = dist_db["sections"].pop(random.randint(0, len(dist_db["sections"]) - 1))
                mia_section_enrollments = [e for e in dist_db["enrollments"] if e["Section_id"] == mia_section["Section_id"]]
                dist_db["enrollments"] = [e for e in dist_db["enrollments"] if e["Section_id"] != mia_section["Section_id"]]
                ec_report("sc_16", f"Section_id: {mia_section['Section_id']}")
            else:
                mia_section = None
                mia_section_enrollments = []

            old_27_id = None
            if len(dist_db["students"]) > 5:
                if ec_active("sc_30"):
                    dist_db["students"][0]["Contact_sis_id"] = f"cont-{uuid.uuid4().hex[:8]}"
                    ec_report("sc_30", f"Student_id: {dist_db['students'][0]['Student_id']}")

                if ec_active("sc_07"):
                    dist_db["students"][2]["Username"] = dist_db["students"][2]["Username"] + "new"
                    ec_report("sc_07", f"Student_id: {dist_db['students'][2]['Student_id']} (UN: {dist_db['students'][2]['Username']})")

                if ec_active("sc_27"):
                    old_27_id = dist_db["students"][3]["Student_id"]
                    dist_db["students"][3]["Student_id"] = f"NEW-{old_27_id}"
                    for e in dist_db["enrollments"]:
                        if e["Student_id"] == old_27_id: e["Student_id"] = dist_db["students"][3]["Student_id"]
                    ec_report("sc_27", f"Original ID: {old_27_id} -> New ID: NEW-{old_27_id}")

                if ec_active("sc_31"):
                    dist_db["students"][4]["Contact_type"] = "Neighbor"
                    ec_report("sc_31", f"Student_id: {dist_db['students'][4]['Student_id']} (Type: Neighbor)")

            export_district_state(config, base_output_dir, dist_name, "Day_2", dist_db)

            # Day 3 mutations
            if mia_student:
                dist_db["students"].append(mia_student)
                dist_db["enrollments"].extend(mia_student_enrollments)
            if mia_section:
                dist_db["sections"].append(mia_section)
                dist_db["enrollments"].extend(mia_section_enrollments)

            if len(dist_db["schools"]) > 1:
                if ec_active("sc_33"):
                    transfer_student = dist_db["students"][1]
                    old_school = transfer_student["School_id"]
                    new_school = next(s["School_id"] for s in dist_db["schools"] if s["School_id"] != old_school)
                    for r in dist_db["students"]:
                        if r["Student_id"] == transfer_student["Student_id"]: r["School_id"] = new_school
                    dist_db["enrollments"] = [e for e in dist_db["enrollments"] if e["Student_id"] != transfer_student["Student_id"]]
                    ec_report("sc_33", f"Student_id: {transfer_student['Student_id']}")

                if ec_active("sc_20") and len(dist_db["sections"]) > 2:
                    scen_20_section = dist_db["sections"][2]
                    old_sec_school = scen_20_section["School_id"]
                    new_sec_school = next(s["School_id"] for s in dist_db["schools"] if s["School_id"] != old_sec_school)
                    scen_20_section["School_id"] = new_sec_school
                    ec_report("sc_20", f"Section_id: {scen_20_section['Section_id']} ({old_sec_school} -> {new_sec_school})")

                if ec_active("sc_34") and len(dist_db["teachers"]) > 2:
                    scen_34_teacher = dist_db["teachers"][2]
                    old_t_school = scen_34_teacher["School_id"]
                    new_t_school = next(s["School_id"] for s in dist_db["schools"] if s["School_id"] != old_t_school)
                    scen_34_teacher["School_id"] = new_t_school
                    ec_report("sc_34", f"Teacher_id: {scen_34_teacher['Teacher_id']} ({old_t_school} -> {new_t_school})")

            # Revert sc_27 SIS ID on Day 3
            if ec_active("sc_27") and old_27_id and len(dist_db["students"]) > 5:
                dist_db["students"][3]["Student_id"] = old_27_id
                for e in dist_db["enrollments"]:
                    if e["Student_id"] == f"NEW-{old_27_id}": e["Student_id"] = old_27_id

            export_district_state(config, base_output_dir, dist_name, "Day_3", dist_db)

        # Write edge case report whenever any edge cases were active
        if active_cases:
            report_path = os.path.join(base_output_dir, f"{dist_name}_edge_cases_report.txt")
            with open(report_path, "w") as f:
                f.write(f"CLEVER DEMO DISTRICT - EDGE CASES REPORT: {dist_name}\n")
                f.write("=========================================================\n\n")
                for scenario, ids in edge_case_report.items():
                    # Only print scenarios that were selected and produced output
                    ec_key = next((ec["key"] for ec in EDGE_CASE_REGISTRY if f"Scenario {ec['number']} ({ec['label']})" == scenario), None)
                    if ec_key and ec_key in active_cases:
                        f.write(f"{scenario}:\n")
                        if not ids: f.write("  None generated in this run.\n")
                        for item in ids: f.write(f"  - {item}\n")
                        f.write("\n")

        if progress_callback: progress_callback((i + 1) / config["NUM_DISTRICTS"])