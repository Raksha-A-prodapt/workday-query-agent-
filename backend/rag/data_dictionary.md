# Workday HR Database Data Dictionary

This document serves as the primary schema knowledge source and data dictionary for the Workday-style HR database (`workday_hr.db`). It provides full table definitions, column specifications, foreign key relationships, business query semantics, and SQL generation rules for schema-aware RAG systems.

---

## 1. Executive Schema Summary

The database is built on SQLite and contains **5 core relational tables**:

1. **`regions`**: Geographical operating regions and country locations (6 records).
2. **`departments`**: Organizational departments, department codes, and annual budgets (8 records).
3. **`employees`**: Employee master data, job titles, department/region assignments, salaries, employment statuses, and manager reporting structure (500 records).
4. **`leave_records`**: Time-off and leave requests, leave types, start/end dates, day counts, and approval statuses (150 records).
5. **`job_openings`**: Requisitions for open, filled, or cancelled job roles with posting/closing dates (50 records).

---

## 2. Table Definitions & Column Specifications

### 2.1 Table: `regions`

#### Purpose
Stores geographical region metadata and country mappings used for regional headcount, payroll, and job opening reporting.

#### Columns
| Column | Type | Key / Constraint | Description | Example / Allowed Values |
| :--- | :--- | :--- | :--- | :--- |
| `region_id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Unique identifier for each region | `1`, `2`, `3` |
| `region_name` | `TEXT` | `NOT NULL`, `UNIQUE` | Human-readable region name | `'North America'`, `'EMEA'`, `'APAC'`, `'LATAM'`, `'India'`, `'DACH'` |
| `country` | `TEXT` | `NOT NULL` | Country associated with the region | `'United States'`, `'United Kingdom'`, `'Singapore'`, `'Brazil'`, `'India'`, `'Germany'` |
| `created_at` | `DATE` | `DEFAULT CURRENT_DATE` | Date region record was created | `'2026-08-20'` |

#### Foreign Key / Parent Relationships
- None (Parent table).
- Referenced by `employees.region_id` and `job_openings.region_id`.

---

### 2.2 Table: `departments`

#### Purpose
Stores organizational department units, department codes, and annual department budgets.

#### Columns
| Column | Type | Key / Constraint | Description | Example / Allowed Values |
| :--- | :--- | :--- | :--- | :--- |
| `department_id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Unique identifier for each department | `1`, `2`, `8` |
| `department_name` | `TEXT` | `NOT NULL`, `UNIQUE` | Full department name | `'Engineering'`, `'Sales'`, `'Human Resources'`, `'Marketing'`, `'Finance'`, `'Product Management'`, `'Customer Support'`, `'Legal & Compliance'` |
| `department_code` | `TEXT` | `NOT NULL`, `UNIQUE` | 3-letter uppercase department code | `'ENG'`, `'SAL'`, `'HR'`, `'MKT'`, `'FIN'`, `'PRD'`, `'SUP'`, `'LGL'` |
| `budget` | `REAL` | Optional | Annual operating budget in USD | `12000000.0`, `8500000.0` |
| `created_at` | `DATE` | `DEFAULT CURRENT_DATE` | Date department record was created | `'2026-08-20'` |

#### Foreign Key / Parent Relationships
- None (Parent table).
- Referenced by `employees.department_id` and `job_openings.department_id`.

---

### 2.3 Table: `employees`

#### Purpose
Central entity table storing employee demographic data, organizational placement, salary, manager hierarchy, and current employment status.

#### Columns
| Column | Type | Key / Constraint | Description | Example / Allowed Values |
| :--- | :--- | :--- | :--- | :--- |
| `employee_id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Unique employee identifier | `1`, `101`, `500` |
| `first_name` | `TEXT` | `NOT NULL` | Employee given name | `'Alex'`, `'Jordan'`, `'Sarah'` |
| `last_name` | `TEXT` | `NOT NULL` | Employee surname | `'Smith'`, `'Johnson'`, `'Patel'` |
| `email` | `TEXT` | `NOT NULL`, `UNIQUE` | Corporate email address | `'alex.smith@workdayhr.com'` |
| `job_title` | `TEXT` | `NOT NULL` | Current functional job title | `'Software Engineer'`, `'Sales Development Rep'`, `'HR Business Partner'` |
| `department_id` | `INTEGER` | `NOT NULL`, `FOREIGN KEY` | References `departments(department_id)` | `1` to `8` |
| `region_id` | `INTEGER` | `NOT NULL`, `FOREIGN KEY` | References `regions(region_id)` | `1` to `6` |
| `manager_id` | `INTEGER` | `FOREIGN KEY` (Self-referential) | References `employees(employee_id)` of manager | `1` (Department Lead) or `NULL` for top executives |
| `hire_date` | `DATE` | `NOT NULL` | Date of employment commencement | `'2021-03-15'` |
| `salary` | `REAL` | `NOT NULL` | Annual base salary in USD | `75000.0`, `145000.0` |
| `employment_status` | `TEXT` | `NOT NULL`, `CHECK` constraint | Current employment status | `'Active'`, `'On Leave'`, `'Terminated'` |

#### Foreign Key Relationships
- `department_id` → `departments(department_id)`
- `region_id` → `regions(region_id)`
- `manager_id` → `employees(employee_id)` (Self-referential hierarchy)
- Referenced by `leave_records.employee_id`.

---

### 2.4 Table: `leave_records`

#### Purpose
Tracks time-off requests, statutory leave, sick leave, and parental leave submitted by employees.

#### Columns
| Column | Type | Key / Constraint | Description | Example / Allowed Values |
| :--- | :--- | :--- | :--- | :--- |
| `leave_id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Unique leave record identifier | `1`, `50`, `150` |
| `employee_id` | `INTEGER` | `NOT NULL`, `FOREIGN KEY` | References `employees(employee_id)` | `1` to `500` |
| `leave_type` | `TEXT` | `NOT NULL`, `CHECK` constraint | Category of leave taken | `'Vacation'`, `'Sick Leave'`, `'Parental Leave'`, `'Unpaid Leave'` |
| `start_date` | `DATE` | `NOT NULL` | Leave start date (`YYYY-MM-DD`) | `'2026-08-10'` |
| `end_date` | `DATE` | `NOT NULL` | Leave end date (`YYYY-MM-DD`) | `'2026-08-25'` |
| `days_count` | `INTEGER` | `NOT NULL` | Total business/calendar days requested | `1` to `30` |
| `approval_status` | `TEXT` | `NOT NULL`, `CHECK` constraint | Status of leave application | `'Approved'`, `'Pending'`, `'Rejected'` |

#### Foreign Key Relationships
- `employee_id` → `employees(employee_id)`

---

### 2.5 Table: `job_openings`

#### Purpose
Stores job requisitions for recruiting, tracking open positions, filled roles, time-to-fill analytics, and hiring pipeline metrics.

#### Columns
| Column | Type | Key / Constraint | Description | Example / Allowed Values |
| :--- | :--- | :--- | :--- | :--- |
| `job_id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Unique job requisition identifier | `1`, `25`, `50` |
| `job_title` | `TEXT` | `NOT NULL` | Title of the position being recruited | `'Senior Software Engineer'`, `'Account Executive'` |
| `department_id` | `INTEGER` | `NOT NULL`, `FOREIGN KEY` | References `departments(department_id)` | `1` to `8` |
| `region_id` | `INTEGER` | `NOT NULL`, `FOREIGN KEY` | References `regions(region_id)` | `1` to `6` |
| `job_status` | `TEXT` | `NOT NULL`, `CHECK` constraint | Current status of the job requisition | `'Open'`, `'Filled'`, `'Cancelled'` |
| `posted_date` | `DATE` | `NOT NULL` | Date job posting went live | `'2026-05-01'` |
| `closed_date` | `DATE` | Optional | Date position was filled or cancelled (`NULL` if `'Open'`) | `'2026-06-15'`, `NULL` |
| `target_hire_count` | `INTEGER` | `DEFAULT 1` | Target number of headcount hires | `1`, `2`, `3` |

#### Foreign Key Relationships
- `department_id` → `departments(department_id)`
- `region_id` → `regions(region_id)`

---

## 3. Entity Relationships Summary

```
regions (1) ───────────< (N) employees (1) ───────────< (N) leave_records
   │                             │ (manager_id)
   │                             └──────┐ (self)
   │                                    ▼
   └───────────< (N) job_openings >────────── (N) <─────────── (1) departments
```

---

## 4. Business Query Guide

This section outlines how common business questions map directly to the SQLite schema definitions.

### 4.1 Employee Headcount Analytics

- **Primary Table**: `employees`
- **Recommended Status Filter**: `employment_status = 'Active'` (for active workforce) or no status filter if total historical headcount is asked.
- **Grouping Dimensions**:
  - `departments.department_name` via `employees.department_id = departments.department_id`
  - `regions.region_name` via `employees.region_id = regions.region_id`
- **Example Business Questions**:
  - *"How many active employees are there?"*
    ```sql
    SELECT COUNT(*) FROM employees WHERE employment_status = 'Active';
    ```
  - *"Show headcount by department."*
    ```sql
    SELECT d.department_name, COUNT(e.employee_id) AS headcount
    FROM departments d
    LEFT JOIN employees e ON d.department_id = e.department_id AND e.employment_status = 'Active'
    GROUP BY d.department_id, d.department_name;
    ```
  - *"Show employee breakdown by region."*
    ```sql
    SELECT r.region_name, COUNT(e.employee_id) AS headcount
    FROM regions r
    LEFT JOIN employees e ON r.region_id = e.region_id AND e.employment_status = 'Active'
    GROUP BY r.region_id, r.region_name;
    ```

---

### 4.2 Employees Currently on Leave

- **Schema Representation**:
  - In the `employees` table: `employment_status = 'On Leave'`.
  - In `leave_records`: Active leave requests have `approval_status = 'Approved'` and date ranges covering the query period (`start_date <= CURRENT_DATE` and `end_date >= CURRENT_DATE`).
- **Primary Logic**:
  - To count or list employees currently marked as on leave: `WHERE employees.employment_status = 'On Leave'`
  - To retrieve leave details (leave type, duration): `JOIN leave_records ON employees.employee_id = leave_records.employee_id WHERE employees.employment_status = 'On Leave' AND leave_records.approval_status = 'Approved'`
- **Example Business Questions**:
  - *"How many employees are currently on leave by region?"*
    ```sql
    SELECT r.region_name, COUNT(e.employee_id) AS on_leave_count
    FROM employees e
    JOIN regions r ON e.region_id = r.region_id
    WHERE e.employment_status = 'On Leave'
    GROUP BY r.region_id, r.region_name;
    ```

---

### 4.3 Leave Analytics & Time-Off Breakdown

- **Primary Table**: `leave_records` (joined with `employees`, `departments`, or `regions` as needed).
- **Categorical Values**:
  - `leave_type`: `'Vacation'`, `'Sick Leave'`, `'Parental Leave'`, `'Unpaid Leave'`
  - `approval_status`: `'Approved'`, `'Pending'`, `'Rejected'`
- **Example Business Questions**:
  - *"What is the breakdown of leave requests by status?"*
    ```sql
    SELECT approval_status, COUNT(*) AS request_count
    FROM leave_records
    GROUP BY approval_status;
    ```
  - *"Total vacation days taken by department."*
    ```sql
    SELECT d.department_name, SUM(l.days_count) AS total_vacation_days
    FROM leave_records l
    JOIN employees e ON l.employee_id = e.employee_id
    JOIN departments d ON e.department_id = d.department_id
    WHERE l.leave_type = 'Vacation' AND l.approval_status = 'Approved'
    GROUP BY d.department_id, d.department_name;
    ```

---

### 4.4 Job Openings & Recruiting Analytics

- **Primary Table**: `job_openings`
- **Categorical Values**:
  - `job_status`: `'Open'`, `'Filled'`, `'Cancelled'`
- **Key Formula - Time-to-Fill (in days)**:
  - Calculated using SQLite's `julianday` function:
    ```sql
    julianday(closed_date) - julianday(posted_date)
    ```
  - Applicable **only** when `job_status = 'Filled'` and `closed_date IS NOT NULL`.
- **Example Business Questions**:
  - *"How many open job positions are there by department?"*
    ```sql
    SELECT d.department_name, COUNT(j.job_id) AS open_jobs
    FROM departments d
    LEFT JOIN job_openings j ON d.department_id = j.department_id AND j.job_status = 'Open'
    GROUP BY d.department_id, d.department_name;
    ```
  - *"What is the average time to fill open roles by department?"*
    ```sql
    SELECT d.department_name,
           ROUND(AVG(julianday(j.closed_date) - julianday(j.posted_date)), 1) AS avg_days_to_fill
    FROM job_openings j
    JOIN departments d ON j.department_id = d.department_id
    WHERE j.job_status = 'Filled' AND j.closed_date IS NOT NULL
    GROUP BY d.department_id, d.department_name;
    ```

---

### 4.5 Compensation & Salary Analytics

- **Primary Table**: `employees`
- **Filters**: Typically filter `employment_status = 'Active'` to reflect current payroll cost.
- **Example Business Questions**:
  - *"What is the average salary by department?"*
    ```sql
    SELECT d.department_name, ROUND(AVG(e.salary), 2) AS avg_salary
    FROM employees e
    JOIN departments d ON e.department_id = d.department_id
    WHERE e.employment_status = 'Active'
    GROUP BY d.department_id, d.department_name;
    ```

---

## 5. SQL Generation Rules for This Schema

### Rule 1: Always Join for Name Fields
Neither `department_name` nor `region_name` exists on the `employees` or `job_openings` tables. Always execute an explicit `JOIN` to `departments` or `regions`.

### Rule 2: Explicit Foreign Key Join Columns
- Join `employees` to `departments`: `ON employees.department_id = departments.department_id`
- Join `employees` to `regions`: `ON employees.region_id = regions.region_id`
- Join `leave_records` to `employees`: `ON leave_records.employee_id = employees.employee_id`
- Join `job_openings` to `departments`: `ON job_openings.department_id = departments.department_id`

### Rule 3: Use SQLite-Compatible Date Functions
Use SQLite `julianday()` for date arithmetic (e.g. `julianday(closed_date) - julianday(posted_date)`). Do not use `DATEDIFF()` or PostgreSQL-specific date operators.

### Rule 4: Self-Join for Managers
`manager_id` on `employees` references `employee_id` on `employees`. To obtain manager names, perform a self-join:
```sql
SELECT e.first_name || ' ' || e.last_name AS employee_name,
       m.first_name || ' ' || m.last_name AS manager_name
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.employee_id;
```

---

## 6. Common Mistakes to Avoid (LLM Anti-Patterns)

| Incorrect / Invalid SQL (❌) | Reason | Correct SQL Solution (✅) |
| :--- | :--- | :--- |
| `SELECT department_name FROM employees` | `department_name` does NOT exist in `employees`. | `SELECT d.department_name FROM employees e JOIN departments d ON e.department_id = d.department_id` |
| `SELECT region_name FROM employees` | `region_name` does NOT exist in `employees`. | `SELECT r.region_name FROM employees e JOIN regions r ON e.region_id = r.region_id` |
| `SELECT DATEDIFF(closed_date, posted_date) FROM job_openings` | `DATEDIFF` is not valid SQLite syntax. | `SELECT (julianday(closed_date) - julianday(posted_date)) FROM job_openings` |
| `SELECT manager_name FROM employees` | `manager_name` column does not exist. | `SELECT m.first_name \|\| ' ' \|\| m.last_name AS manager_name FROM employees e JOIN employees m ON e.manager_id = m.employee_id` |
| `SELECT SUM(salary) FROM employees` | Includes terminated employees if unfiltered. | `SELECT SUM(salary) FROM employees WHERE employment_status = 'Active'` |
| `SELECT * FROM t ORDER BY c LIMIT 1 UNION ALL SELECT * FROM t ORDER BY c ASC LIMIT 1` | `ORDER BY` cannot come before `UNION ALL` in raw SQLite subqueries without subquery wrapping or CTEs. | `SELECT * FROM (SELECT * FROM t ORDER BY c DESC LIMIT 1) UNION ALL SELECT * FROM (SELECT * FROM t ORDER BY c ASC LIMIT 1)` |

