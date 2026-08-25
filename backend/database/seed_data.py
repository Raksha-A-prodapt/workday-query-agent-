"""
Synthetic Data Generator for Workday-Style HR Database.
Fills workday_hr.db with realistic HR analytical data.
"""

import os
import random
import sqlite3
from datetime import datetime, timedelta

# Seed for reproducibility
random.seed(42)

FIRST_NAMES = [
    "Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Avery", "Peyton",
    "Quinn", "Skyler", "Dakota", "Reese", "Rowan", "Emerson", "Finley", "Hayden",
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
    "Matthew", "Betty", "Anthony", "Margaret", "Donald", "Sandra", "Mark", "Ashley",
    "Paul", "Kimberly", "Steven", "Emily", "Andrew", "Donna", "Kenneth", "Michelle",
    "Joshua", "Carol", "Kevin", "Amanda", "Brian", "Melissa", "George", "Deborah",
    "Edward", "Stephanie", "Ronald", "Rebecca", "Timothy", "Sharon", "Jason", "Laura",
    "Jeffrey", "Cynthia", "Ryan", "Kathleen", "Jacob", "Amy", "Gary", "Shirley",
    "Nicholas", "Angela", "Eric", "Helen", "Jonathan", "Anna", "Stephen", "Brenda",
    "Larry", "Pamela", "Justin", "Nicole", "Scott", "Samantha", "Brandon", "Katherine",
    "Benjamin", "Emma", "Samuel", "Christine", "Gregory", "Debra", "Alexander", "Rachel",
    "Frank", "Catherine", "Patrick", "Carolyn", "Raymond", "Janet", "Jack", "Ruth",
    "Dennis", "Maria", "Jerry", "Heather", "Tyler", "Diane", "Aaron", "Virginia",
    "Jose", "Julie", "Adam", "Joyce", "Nathan", "Victoria", "Henry", "Olivia",
    "Zachary", "Kelly", "Douglas", "Christina", "Peter", "Lauren", "Kyle", "Joan",
    "Noah", "Evelyn", "Ethan", "Judith", "Jeremy", "Megan", "Christian", "Cheryl",
    "Walter", "Andrea", "Keith", "Hannah", "Austin", "Martha", "Roger", "Jacqueline",
    "Terry", "Frances", "Sean", "Gloria", "Gerald", "Ann", "Carl", "Teresa",
    "Dylan", "Kathryn", "Harold", "Sara", "Jordan", "Janice", "Jesse", "Jean",
    "Bryan", "Alice", "Lawrence", "Madison", "Arthur", "Doris", "Gabriel", "Abigail",
    "Bruce", "Julia", "Logan", "Judy", "Billy", "Grace", "Joe", "Denise",
    "Alan", "Amber", "Juan", "Marilyn", "Albert", "Beverly", "Willie", "Danielle",
    "Elijah", "Theresa", "Wayne", "Sophia", "Roy", "Marie", "Ralph", "Diana",
    "Randy", "Brittany", "Eugene", "Natalie", "Vincent", "Isabella", "Russell", "Charlotte"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
    "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White",
    "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young",
    "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker",
    "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales", "Murphy",
    "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper", "Peterson", "Bailey",
    "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson",
    "Watson", "Brooks", "Chavez", "Wood", "James", "Bennett", "Gray", "Mendoza",
    "Ruiz", "Hughes", "Price", "Alvarez", "Castillo", "Sanders", "Patel", "Myers",
    "Long", "Ross", "Foster", "Jimenez", "Powell", "Jenkins", "Perry", "Russell",
    "Sullivan", "Bell", "Coleman", "Butler", "Henderson", "Barnes", "Gonzales", "Fisher",
    "Vasquez", "Simmons", "Romero", "Jordan", "Patterson", "Alexander", "Hamilton", "Graham",
    "Reynolds", "Griffin", "Wallace", "Moreno", "West", "Cole", "Hayes", "Bryant",
    "Herrera", "Gibson", "Ellis", "Tran", "Medina", "Aguilar", "Stevens", "Murray",
    "Ford", "Castro", "Marshall", "Owens", "Harrison", "Fernandez", "McDonald", "Woods",
    "Washington", "Kennedy", "Wells", "Vargas", "Henry", "Chen", "Freeman", "Webb",
    "Tucker", "Guzman", "Burns", "Crawford", "Olson", "Simpson", "Porter", "Hunter",
    "Gordon", "Mendez", "Silva", "Shaw", "Snyder", "Mason", "Dixon", "Mueller"
]

DEPARTMENTS = [
    ("Engineering", "ENG", 12000000.0),
    ("Sales", "SAL", 8500000.0),
    ("Human Resources", "HR", 3000000.0),
    ("Marketing", "MKT", 4500000.0),
    ("Finance", "FIN", 5000000.0),
    ("Product Management", "PRD", 6000000.0),
    ("Customer Support", "SUP", 3500000.0),
    ("Legal & Compliance", "LGL", 2500000.0)
]

REGIONS = [
    ("North America", "United States"),
    ("EMEA", "United Kingdom"),
    ("APAC", "Singapore"),
    ("LATAM", "Brazil"),
    ("India", "India"),
    ("DACH", "Germany")
]

JOB_TITLES_BY_DEPT = {
    "Engineering": [
        "Software Engineer", "Senior Software Engineer", "Staff Engineer",
        "DevOps Engineer", "QA Engineer", "Engineering Manager"
    ],
    "Sales": [
        "Account Executive", "Senior Account Executive", "Sales Development Rep",
        "Sales Manager", "Solutions Architect"
    ],
    "Human Resources": [
        "HR Coordinator", "HR Business Partner", "Talent Acquisition Specialist",
        "HR Director"
    ],
    "Marketing": [
        "Marketing Specialist", "Content Strategist", "Growth Marketing Lead",
        "Marketing Manager"
    ],
    "Finance": [
        "Financial Analyst", "Senior Accountant", "Finance Manager", "Payroll Specialist"
    ],
    "Product Management": [
        "Product Manager", "Senior Product Manager", "UX Designer", "Product Lead"
    ],
    "Customer Support": [
        "Support Specialist", "Senior Support Engineer", "Customer Success Manager"
    ],
    "Legal & Compliance": [
        "Legal Counsel", "Compliance Officer", "Paralegal"
    ]
}


def seed_database(db_path: str):
    """Seed the SQLite database with 500+ employees, 150+ leave records, 50+ job openings."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Insert Regions
    region_ids = []
    for name, country in REGIONS:
        cursor.execute(
            "INSERT INTO regions (region_name, country) VALUES (?, ?);",
            (name, country)
        )
        region_ids.append(cursor.lastrowid)

    # 2. Insert Departments
    dept_ids = []
    dept_name_map = {}
    for name, code, budget in DEPARTMENTS:
        cursor.execute(
            "INSERT INTO departments (department_name, department_code, budget) VALUES (?, ?, ?);",
            (name, code, budget)
        )
        dept_id = cursor.lastrowid
        dept_ids.append(dept_id)
        dept_name_map[dept_id] = name

    # 3. Insert Employees (500)
    employee_ids = []
    dept_managers = {}  # dept_id -> manager_employee_id
    
    # Generate department managers first
    for dept_id in dept_ids:
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        email = f"{fn.lower()}.{ln.lower()}.mgr{dept_id}@workdayhr.com"
        title = f"{dept_name_map[dept_id]} Director"
        region_id = random.choice(region_ids)
        hire_date = (datetime(2018, 1, 1) + timedelta(days=random.randint(0, 1000))).strftime("%Y-%m-%d")
        salary = round(random.uniform(140000, 195000), 2)
        status = "Active"

        cursor.execute(
            """
            INSERT INTO employees (first_name, last_name, email, job_title, department_id, region_id, manager_id, hire_date, salary, employment_status)
            VALUES (?, ?, ?, ?, ?, ?, NULL, ?, ?, ?);
            """,
            (fn, ln, email, title, dept_id, region_id, hire_date, salary, status)
        )
        mgr_id = cursor.lastrowid
        employee_ids.append(mgr_id)
        dept_managers[dept_id] = mgr_id

    # Generate remaining 492 employees
    email_set = set(e[2] for e in cursor.execute("SELECT first_name, last_name, email FROM employees").fetchall())

    statuses = ["Active"] * 417 + ["On Leave"] * 50 + ["Terminated"] * 25  # Total 492 + 8 = 500
    random.shuffle(statuses)

    for i in range(492):
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        base_email = f"{fn.lower()}.{ln.lower()}{i+1}@workdayhr.com"
        while base_email in email_set:
            base_email = f"{fn.lower()}.{ln.lower()}{random.randint(100,9999)}@workdayhr.com"
        email_set.add(base_email)

        dept_id = random.choice(dept_ids)
        dept_name = dept_name_map[dept_id]
        title = random.choice(JOB_TITLES_BY_DEPT[dept_name])
        region_id = random.choice(region_ids)
        manager_id = dept_managers[dept_id]

        hire_days_ago = random.randint(100, 2500)
        hire_date = (datetime.now() - timedelta(days=hire_days_ago)).strftime("%Y-%m-%d")
        salary = round(random.uniform(55000, 150000), 2)
        status = statuses[i]

        cursor.execute(
            """
            INSERT INTO employees (first_name, last_name, email, job_title, department_id, region_id, manager_id, hire_date, salary, employment_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (fn, ln, base_email, title, dept_id, region_id, manager_id, hire_date, salary, status)
        )
        employee_ids.append(cursor.lastrowid)

    # 4. Insert Leave Records (150)
    # Ensure all "On Leave" employees have an active/recent leave record in 2026-08
    on_leave_employees = [
        row[0] for row in cursor.execute(
            "SELECT employee_id FROM employees WHERE employment_status = 'On Leave'"
        ).fetchall()
    ]
    active_employees = [
        row[0] for row in cursor.execute(
            "SELECT employee_id FROM employees WHERE employment_status = 'Active'"
        ).fetchall()
    ]

    leave_types = ["Vacation", "Sick Leave", "Parental Leave", "Unpaid Leave"]
    current_date = datetime(2026, 8, 15)

    # Active leave for all "On Leave" employees (50 records)
    for emp_id in on_leave_employees:
        l_type = random.choice(leave_types)
        days_before = random.randint(1, 10)
        days_after = random.randint(5, 20)
        start_d = current_date - timedelta(days=days_before)
        end_d = current_date + timedelta(days=days_after)
        days_cnt = (end_d - start_d).days + 1

        cursor.execute(
            """
            INSERT INTO leave_records (employee_id, leave_type, start_date, end_date, days_count, approval_status)
            VALUES (?, ?, ?, ?, ?, 'Approved');
            """,
            (emp_id, l_type, start_d.strftime("%Y-%m-%d"), end_d.strftime("%Y-%m-%d"), days_cnt)
        )

    # Historical/Pending/Rejected leave for active employees (100 records)
    for _ in range(100):
        emp_id = random.choice(active_employees)
        l_type = random.choice(leave_types)
        offset = random.randint(-180, 60)
        start_d = current_date + timedelta(days=offset)
        duration = random.randint(1, 14)
        end_d = start_d + timedelta(days=duration)
        days_cnt = duration + 1
        status = random.choices(["Approved", "Pending", "Rejected"], weights=[80, 15, 5])[0]

        cursor.execute(
            """
            INSERT INTO leave_records (employee_id, leave_type, start_date, end_date, days_count, approval_status)
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            (emp_id, l_type, start_d.strftime("%Y-%m-%d"), end_d.strftime("%Y-%m-%d"), days_cnt, status)
        )

    # 5. Insert Job Openings (50)
    job_statuses = ["Open"] * 20 + ["Filled"] * 25 + ["Cancelled"] * 5
    random.shuffle(job_statuses)

    for i in range(50):
        dept_id = random.choice(dept_ids)
        dept_name = dept_name_map[dept_id]
        title = random.choice(JOB_TITLES_BY_DEPT[dept_name])
        region_id = random.choice(region_ids)
        status = job_statuses[i]

        posted_days_ago = random.randint(30, 200)
        posted_d = current_date - timedelta(days=posted_days_ago)
        posted_str = posted_d.strftime("%Y-%m-%d")

        if status == "Filled":
            time_to_fill = random.randint(15, 90)
            closed_d = posted_d + timedelta(days=time_to_fill)
            closed_str = closed_d.strftime("%Y-%m-%d")
        elif status == "Cancelled":
            closed_d = posted_d + timedelta(days=random.randint(5, 30))
            closed_str = closed_d.strftime("%Y-%m-%d")
        else:
            closed_str = None

        target_hires = random.choice([1, 1, 1, 2, 3])

        cursor.execute(
            """
            INSERT INTO job_openings (job_title, department_id, region_id, job_status, posted_date, closed_date, target_hire_count)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            (title, dept_id, region_id, status, posted_str, closed_str, target_hires)
        )

    conn.commit()
    conn.close()
    print("Database seeding completed successfully.")


if __name__ == "__main__":
    db_file = os.path.join(os.path.dirname(__file__), "workday_hr.db")
    seed_database(db_file)
