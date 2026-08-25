"""
Unit and Integration Tests for Workday HR SQLite Database.
Verifies database integrity, record thresholds, foreign keys, and 10+ analytical HR queries.
"""

import os
import sqlite3
import unittest

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "workday_hr.db")


class TestWorkdayDatabase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Ensure database exists before running tests."""
        cls.db_path = os.path.abspath(DB_PATH)
        assert os.path.exists(cls.db_path), f"Database file not found at {cls.db_path}"

    def get_connection(self):
        """Get database connection with foreign keys enabled."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def test_01_database_file_exists(self):
        """Test database file exists and is non-empty."""
        self.assertTrue(os.path.exists(self.db_path))
        self.assertGreater(os.path.getsize(self.db_path), 0)

    def test_02_required_tables_exist(self):
        """Test all 5 required tables exist in SQLite master."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = set(row[0] for row in cursor.fetchall())
        conn.close()

        expected_tables = {"regions", "departments", "employees", "leave_records", "job_openings"}
        self.assertTrue(expected_tables.issubset(tables), f"Missing tables: {expected_tables - tables}")

    def test_03_record_counts_meet_minimums(self):
        """Test record counts satisfy required minimum thresholds."""
        conn = self.get_connection()
        cursor = conn.cursor()

        thresholds = {
            "regions": 6,
            "departments": 8,
            "employees": 500,
            "leave_records": 150,
            "job_openings": 50
        }

        for table, min_count in thresholds.items():
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            self.assertGreaterEqual(
                count, min_count,
                f"Table {table} has {count} records, expected at least {min_count}"
            )
        conn.close()

    def test_04_foreign_key_integrity(self):
        """Test PRAGMA foreign_key_check returns zero violations."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_key_check;")
        violations = cursor.fetchall()
        conn.close()

        self.assertEqual(len(violations), 0, f"Foreign key violations detected: {violations}")

    def test_05_query_total_employee_count(self):
        """1. Query: Total employee count."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM employees;")
        res = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(res)
        self.assertGreaterEqual(res[0], 500)

    def test_06_query_employees_by_department(self):
        """2. Query: Employees count by department."""
        sql = """
        SELECT d.department_name, COUNT(e.employee_id) AS total_employees
        FROM departments d
        LEFT JOIN employees e ON d.department_id = e.department_id
        GROUP BY d.department_id, d.department_name
        ORDER BY total_employees DESC;
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.close()

        self.assertEqual(len(rows), 8)
        for dept_name, count in rows:
            self.assertGreater(count, 0)

    def test_07_query_employees_by_region(self):
        """3. Query: Employees count by region."""
        sql = """
        SELECT r.region_name, COUNT(e.employee_id) AS total_employees
        FROM regions r
        LEFT JOIN employees e ON r.region_id = e.region_id
        GROUP BY r.region_id, r.region_name
        ORDER BY total_employees DESC;
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.close()

        self.assertEqual(len(rows), 6)
        for reg_name, count in rows:
            self.assertGreater(count, 0)

    def test_08_query_employees_currently_on_leave(self):
        """4. Query: Active employees currently on leave."""
        sql = """
        SELECT e.employee_id, e.first_name, e.last_name, d.department_name, r.region_name
        FROM employees e
        JOIN departments d ON e.department_id = d.department_id
        JOIN regions r ON e.region_id = r.region_id
        WHERE e.employment_status = 'On Leave';
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.close()

        self.assertGreater(len(rows), 0)

    def test_09_query_leave_count_by_region(self):
        """5. Query: Leave count by region."""
        sql = """
        SELECT r.region_name, COUNT(l.leave_id) AS total_leaves
        FROM regions r
        JOIN employees e ON r.region_id = e.region_id
        JOIN leave_records l ON e.employee_id = l.employee_id
        GROUP BY r.region_id, r.region_name
        ORDER BY total_leaves DESC;
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.close()

        self.assertGreater(len(rows), 0)

    def test_10_query_open_jobs_by_department(self):
        """6. Query: Open job openings count by department."""
        sql = """
        SELECT d.department_name, COUNT(j.job_id) AS open_jobs
        FROM departments d
        LEFT JOIN job_openings j ON d.department_id = j.department_id AND j.job_status = 'Open'
        GROUP BY d.department_id, d.department_name
        ORDER BY open_jobs DESC;
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.close()

        self.assertEqual(len(rows), 8)

    def test_11_query_avg_time_to_fill(self):
        """7. Query: Average time to fill closed job roles (in days) by department."""
        sql = """
        SELECT d.department_name,
               ROUND(AVG(julianday(j.closed_date) - julianday(j.posted_date)), 1) AS avg_days_to_fill
        FROM job_openings j
        JOIN departments d ON j.department_id = d.department_id
        WHERE j.job_status = 'Filled' AND j.closed_date IS NOT NULL
        GROUP BY d.department_id, d.department_name
        ORDER BY avg_days_to_fill ASC;
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.close()

        self.assertGreater(len(rows), 0)
        for dept_name, avg_days in rows:
            self.assertGreater(avg_days, 0)

    def test_12_query_avg_salary_by_dept_region(self):
        """8. Query: Average salary by department and region."""
        sql = """
        SELECT d.department_name, r.region_name, ROUND(AVG(e.salary), 2) AS avg_salary
        FROM employees e
        JOIN departments d ON e.department_id = d.department_id
        JOIN regions r ON e.region_id = r.region_id
        WHERE e.employment_status = 'Active'
        GROUP BY d.department_name, r.region_name
        ORDER BY avg_salary DESC;
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.close()

        self.assertGreater(len(rows), 0)

    def test_13_query_leave_by_type_and_status(self):
        """9. Query: Leave record breakdown by leave type and approval status."""
        sql = """
        SELECT leave_type, approval_status, COUNT(*) AS count
        FROM leave_records
        GROUP BY leave_type, approval_status
        ORDER BY leave_type, approval_status;
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.close()

        self.assertGreater(len(rows), 0)

    def test_14_query_top_departments_by_active_employee_count(self):
        """10. Query: Top departments by active employee count and total salary cost."""
        sql = """
        SELECT d.department_name,
               COUNT(e.employee_id) AS active_employees,
               SUM(e.salary) AS total_payroll
        FROM departments d
        JOIN employees e ON d.department_id = e.department_id
        WHERE e.employment_status = 'Active'
        GROUP BY d.department_id, d.department_name
        ORDER BY active_employees DESC;
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.close()

        self.assertEqual(len(rows), 8)


if __name__ == "__main__":
    unittest.main()
