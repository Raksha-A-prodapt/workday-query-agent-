-- SQLite Schema for Workday-Style HR Database

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS leave_records;
DROP TABLE IF EXISTS job_openings;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS departments;
DROP TABLE IF EXISTS regions;

-- 1. Regions
CREATE TABLE regions (
    region_id INTEGER PRIMARY KEY AUTOINCREMENT,
    region_name TEXT NOT NULL UNIQUE,
    country TEXT NOT NULL,
    created_at DATE DEFAULT CURRENT_DATE
);

-- 2. Departments
CREATE TABLE departments (
    department_id INTEGER PRIMARY KEY AUTOINCREMENT,
    department_name TEXT NOT NULL UNIQUE,
    department_code TEXT NOT NULL UNIQUE,
    budget REAL,
    created_at DATE DEFAULT CURRENT_DATE
);

-- 3. Employees
CREATE TABLE employees (
    employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    job_title TEXT NOT NULL,
    department_id INTEGER NOT NULL,
    region_id INTEGER NOT NULL,
    manager_id INTEGER,
    hire_date DATE NOT NULL,
    salary REAL NOT NULL,
    employment_status TEXT NOT NULL CHECK (employment_status IN ('Active', 'On Leave', 'Terminated')),
    FOREIGN KEY (department_id) REFERENCES departments(department_id),
    FOREIGN KEY (region_id) REFERENCES regions(region_id),
    FOREIGN KEY (manager_id) REFERENCES employees(employee_id)
);

-- 4. Leave Records
CREATE TABLE leave_records (
    leave_id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    leave_type TEXT NOT NULL CHECK (leave_type IN ('Vacation', 'Sick Leave', 'Parental Leave', 'Unpaid Leave')),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    days_count INTEGER NOT NULL,
    approval_status TEXT NOT NULL CHECK (approval_status IN ('Approved', 'Pending', 'Rejected')),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

-- 5. Job Openings
CREATE TABLE job_openings (
    job_id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_title TEXT NOT NULL,
    department_id INTEGER NOT NULL,
    region_id INTEGER NOT NULL,
    job_status TEXT NOT NULL CHECK (job_status IN ('Open', 'Filled', 'Cancelled')),
    posted_date DATE NOT NULL,
    closed_date DATE,
    target_hire_count INTEGER DEFAULT 1,
    FOREIGN KEY (department_id) REFERENCES departments(department_id),
    FOREIGN KEY (region_id) REFERENCES regions(region_id)
);

-- Performance Indexes
CREATE INDEX idx_employees_dept ON employees(department_id);
CREATE INDEX idx_employees_region ON employees(region_id);
CREATE INDEX idx_employees_status ON employees(employment_status);
CREATE INDEX idx_leave_emp ON leave_records(employee_id);
CREATE INDEX idx_leave_dates ON leave_records(start_date, end_date);
CREATE INDEX idx_job_dept ON job_openings(department_id);
CREATE INDEX idx_job_status ON job_openings(job_status);
