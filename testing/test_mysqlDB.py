import re
import unittest
from unittest.mock import MagicMock, patch, mock_open, call
import mysql
from classes.employee import Employee
from classes.general_info import GeneralInfo
from classes.personal_info import PersonalInfo
from classes.salary import Salary
from databases.mysqlDB import MySQL
from datetime import date
import json

class TestMySQL(unittest.TestCase):

    @patch('databases.mysqlDB.mysql.connector.connect')
    def setUp(self, mock_connect):
        self.mock_connection = MagicMock()
        mock_connect.return_value = self.mock_connection

        self.mock_cursor = MagicMock()
        self.mock_connection.cursor.return_value = self.mock_cursor

        with patch.object(MySQL, 'create_tables'), \
             patch.object(MySQL, 'check_and_insert_departments'), \
             patch.object(MySQL, 'create_trigger_calculate_experience_generalinfo'), \
             patch.object(MySQL, 'create_update_duration_trigger'):
            self.mysql = MySQL()

    def normalize_sql(self, sql):
        return re.sub(r'\s+', ' ', sql.strip())

    def test_create_tables(self):
        self.mysql.create_tables()

        expected_calls = [
            "CREATE TABLE IF NOT EXISTS Employee ( employee_id VARCHAR(36) PRIMARY KEY, full_name VARCHAR(255) NOT NULL )",
            "CREATE TABLE IF NOT EXISTS Departments ( department_id INT PRIMARY KEY AUTO_INCREMENT, department_name VARCHAR(255) NOT NULL, department_positions INT DEFAULT 0, average_salary DECIMAL(10, 2) DEFAULT 0.00 )",
            "CREATE TABLE IF NOT EXISTS Positions ( position_id INT PRIMARY KEY AUTO_INCREMENT, department_id INT NOT NULL, position_name VARCHAR(255) NOT NULL, salary_amount DECIMAL(10, 2) NOT NULL, FOREIGN KEY (department_id) REFERENCES Departments(department_id) ON DELETE CASCADE )",
            "CREATE TABLE IF NOT EXISTS Company ( company_name VARCHAR(255) PRIMARY KEY, num_of_departments INT DEFAULT 0 )",
            "CREATE TABLE IF NOT EXISTS GeneralInfo ( employee_id VARCHAR(36) PRIMARY KEY, department_id INT NOT NULL, position_id INT NOT NULL, hire_date DATE NOT NULL, previous_experience INT DEFAULT 0, total_experience INT DEFAULT 0, FOREIGN KEY (employee_id) REFERENCES Employee(employee_id) ON DELETE CASCADE, FOREIGN KEY (department_id) REFERENCES Departments(department_id), FOREIGN KEY (position_id) REFERENCES Positions(position_id) )",
            "CREATE TABLE IF NOT EXISTS PersonalInfo ( employee_id VARCHAR(36) PRIMARY KEY, birth_date DATE NOT NULL, sex ENUM('Male', 'Female'), number_of_children INT DEFAULT 0, phone_number VARCHAR(15), marital_status ENUM('', 'Single', 'Married'), email VARCHAR(255), FOREIGN KEY (employee_id) REFERENCES Employee(employee_id) ON DELETE CASCADE )",
            "CREATE TABLE IF NOT EXISTS Salary ( employee_id VARCHAR(36), salary_month VARCHAR(7) NOT NULL, salary_amount DECIMAL(10, 2) NOT NULL, PRIMARY KEY (employee_id, salary_month), FOREIGN KEY (employee_id) REFERENCES Employee(employee_id) ON DELETE CASCADE )",
            "CREATE TABLE IF NOT EXISTS Leaves ( leave_id INT AUTO_INCREMENT PRIMARY KEY, employee_id VARCHAR(36) NOT NULL, leave_type ENUM('Sick', 'Vacation', 'Time Off') NOT NULL, start_date DATE NOT NULL, end_date DATE NOT NULL, duration INT GENERATED ALWAYS AS (DATEDIFF(end_date, start_date) + 1), FOREIGN KEY (employee_id) REFERENCES Employee(employee_id) ON DELETE CASCADE )",
        ]

        actual_calls = [call[0][0] for call in self.mock_cursor.execute.call_args_list]

        for expected_call in expected_calls:
            normalized_expected = self.normalize_sql(expected_call)
            self.assertTrue(
                any(normalized_expected == self.normalize_sql(actual) for actual in actual_calls),
                f"Expected SQL call not found: {normalized_expected}"
            )

        self.mock_connection.commit.assert_called_once()

    def test_add_employee(self):
        employee = Employee("123", "John Doe")

        self.mysql.add_employee(employee)

        self.mock_cursor.execute.assert_called_once_with(
            "INSERT INTO Employee (employee_id, full_name) VALUES (%s, %s)",
            ("123", "John Doe")
        )
        self.mock_connection.commit.assert_called_once()
        self.mock_cursor.close.assert_called_once()

    def test_add_general_info(self):
        general_info = GeneralInfo(
            employee_id="123",
            department_id=1,
            position_id=2,
            hire_date=date(2024, 4, 27),
            experience=5
        )

        self.mysql.add_general_info(general_info)

        self.mock_cursor.execute.assert_any_call(
            unittest.mock.ANY,
            ("123", 1, 2, date(2024, 4, 27), 5)
        )
        self.mock_connection.commit.assert_called_once()
        self.mock_cursor.close.assert_called_once()

    def test_add_personal_info(self):
        personal_info = PersonalInfo(
            employee_id="123",
            birth_date=date(1990, 1, 1),
            sex="Male",
            number_of_children=2,
            phone_number="1234567890",
            marital_status="Married",
            email="johndoe@example.com"
        )

        self.mysql.add_personal_info(personal_info)

        self.mock_cursor.execute.assert_any_call(
            unittest.mock.ANY,
            ("123", date(1990, 1, 1), "Male", 2, "1234567890", "Married", "johndoe@example.com")
        )
        self.mock_connection.commit.assert_called_once()
        self.mock_cursor.close.assert_called_once()

    def test_add_employee_salary(self):
        salary = Salary(employee_id="123", month="2024-04", salary=5000.75)

        self.mysql.add_employee_salary(salary)

        expected_query = self.normalize_sql("""
            INSERT INTO Salary (employee_id, salary_month, salary_amount)
            VALUES (%s, %s, %s)
        """)

        actual_query = self.normalize_sql(self.mock_cursor.execute.call_args[0][0])

        self.assertEqual(expected_query, actual_query)
        self.assertEqual(self.mock_cursor.execute.call_args[0][1], ("123", "2024-04", 5000.75))
        self.mock_connection.commit.assert_called_once()
        self.mock_cursor.close.assert_called_once()

    def test_add_leave_request(self):
        self.mysql.add_leave_request("123", "Vacation", date(2024, 5, 1), date(2024, 5, 10))

        expected_query = self.normalize_sql("""
            INSERT INTO Leaves (employee_id, leave_type, start_date, end_date)
            VALUES (%s, %s, %s, %s)
        """)

        actual_query = self.normalize_sql(self.mock_cursor.execute.call_args[0][0])

        self.assertEqual(expected_query, actual_query)
        self.assertEqual(self.mock_cursor.execute.call_args[0][1], ("123", "Vacation", date(2024, 5, 1), date(2024, 5, 10)))
        self.mock_connection.commit.assert_called_once()
        self.mock_cursor.close.assert_called_once()

    def test_delete_worker_by_id(self):
        self.mysql.delete_worker_by_id("123")

        self.mysql.cursor.execute.assert_called_once_with(
            "DELETE FROM Employee WHERE employee_id = %s",
            ("123",)
        )
        self.mysql.mydb.commit.assert_called_once()

    def test_delete_leave_request(self):
        self.mysql.delete_leave_request("123", "Sick", date(2024, 5, 1), date(2024, 5, 5))

        expected_query = self.normalize_sql("""
            DELETE FROM Leaves
            WHERE employee_id = %s AND leave_type = %s AND start_date = %s AND end_date = %s
        """)

        actual_query = self.normalize_sql(self.mock_cursor.execute.call_args[0][0])

        self.assertEqual(expected_query, actual_query)
        self.assertEqual(
            self.mock_cursor.execute.call_args[0][1],
            ("123", "Sick", date(2024, 5, 1), date(2024, 5, 5))
        )
        self.mock_connection.commit.assert_called_once()
        self.mock_cursor.close.assert_called_once()

    def test_update_employee(self):
        data = {
            "employee_id": "123",
            "full_name": "John Doe",
            "department_id": 1,
            "position_id": 2,
            "hire_date": date(2024, 4, 27),
            "experience": 5,
            "birth_date": date(1990, 1, 1),
            "sex": "Male",
            "phone_number": "123456789",
            "marital_status": "Single",
            "email": "john.doe@example.com"
        }

        result = self.mysql.update_employee(data)

        self.assertTrue(result)
        self.mock_connection.commit.assert_called_once()
        self.assertEqual(self.mock_cursor.execute.call_count, 3)

    def test_update_personal_info(self):
        data = {
            "employee_id": "123",
            "number_of_children": 2,
            "marital_status": "Married",
            "phone_number": "123456789",
            "email": "john.doe@example.com"
        }

        result = self.mysql.update_personal_info(data)

        self.assertTrue(result)

        expected_query = self.normalize_sql("""
            UPDATE PersonalInfo
            SET number_of_children = %s, marital_status = %s, phone_number = %s, email = %s
            WHERE employee_id = %s
        """)

        actual_query = self.normalize_sql(self.mock_cursor.execute.call_args[0][0])

        self.assertEqual(expected_query, actual_query)
        self.assertEqual(
            self.mock_cursor.execute.call_args[0][1],
            (2, "Married", "123456789", "john.doe@example.com", "123")
        )
        self.mock_connection.commit.assert_called_once()

    def test_update_leave_request(self):
        self.mysql.update_leave_request("123", "Vacation", date(2024, 5, 1), date(2024, 5, 10))

        expected_query = self.normalize_sql("""
            UPDATE Leaves 
            SET leave_type = %s, start_date = %s, end_date = %s 
            WHERE employee_id = %s
        """)

        actual_query = self.normalize_sql(self.mock_cursor.execute.call_args[0][0])

        self.assertEqual(expected_query, actual_query)
        self.assertEqual(
            self.mock_cursor.execute.call_args[0][1],
            ("Vacation", date(2024, 5, 1), date(2024, 5, 10), "123")
        )
        self.mock_connection.commit.assert_called_once()
        self.mock_cursor.close.assert_called_once()

    def test_update_user_email(self):
        self.mysql.update_user_email("123", "john.doe@example.com")

        self.mock_cursor.execute.assert_called_once_with(
            "UPDATE PersonalInfo SET email = %s WHERE employee_id = %s",
            ("john.doe@example.com", "123")
        )
        self.mock_connection.commit.assert_called_once()

    def test_get_employee_id_by_name(self):
        self.mock_cursor.fetchone.return_value = ("123",)

        result = self.mysql.get_employee_id_by_name("John Doe")

        self.mock_cursor.execute.assert_called_once_with(
            "SELECT employee_id FROM Employee WHERE full_name = %s",
            ("John Doe",)
        )
        self.assertEqual(result, "123")
        self.mock_cursor.close.assert_called_once()

    def test_get_all_workers(self):
        self.mock_cursor.fetchall.return_value = [("123", "John Doe"), ("456", "Jane Smith")]

        result = self.mysql.get_all_workers()

        self.mock_cursor.execute.assert_called_once_with("SELECT employee_id, full_name FROM Employee")
        self.assertEqual(result, [("123", "John Doe"), ("456", "Jane Smith")])
        self.mock_cursor.close.assert_called_once()

    def test_get_email_by_id(self):
        self.mock_cursor.fetchone.return_value = ("john.doe@example.com",)

        result = self.mysql.get_email_by_id("123")

        self.mock_cursor.execute.assert_called_once_with(
            "SELECT email FROM PersonalInfo WHERE employee_id = %s",
            ("123",)
        )
        self.assertEqual(result, "john.doe@example.com")

    def test_get_email_by_id_invalid(self):
        self.mock_cursor.fetchone.return_value = ("invalidemail",)

        result = self.mysql.get_email_by_id("123")

        self.mock_cursor.execute.assert_called_once_with(
            "SELECT email FROM PersonalInfo WHERE employee_id = %s",
            ("123",)
        )
        self.assertEqual(result, 0)

    def test_get_all_leave_requests(self):
        self.mock_cursor.fetchall.return_value = [
            ("John Doe", "Vacation", "2024-05-01", "2024-05-10", 10)
        ]

        result = self.mysql.get_all_leave_requests()

        expected_query = """SELECT e.full_name, l.leave_type, l.start_date, l.end_date, l.duration
                            FROM Leaves l
                            JOIN Employee e ON l.employee_id = e.employee_id"""

        actual_call = self.mock_cursor.execute.call_args[0][0]
        self.assertEqual(self.normalize_sql(actual_call), self.normalize_sql(expected_query))

        self.assertEqual(result, [
            ("John Doe", "Vacation", "2024-05-01", "2024-05-10", 10)
        ])

    def test_get_worker_details(self):
        self.mysql.get_worker_details("123")

        self.mock_cursor.execute.assert_any_call(
            unittest.mock.ANY,
            ("123",)
        )

    def test_get_all_salaries_with_names(self):
        self.mock_cursor.fetchall.return_value = [
            ("John Doe", "2024-05", 5000.75),
            ("Jane Smith", "2024-04", 4500.50)
        ]

        result = self.mysql.get_all_salaries_with_names()

        self.mock_cursor.execute.assert_called_once_with("""
            SELECT e.full_name, s.salary_month, s.salary_amount
            FROM Salary s
            JOIN Employee e ON s.employee_id = e.employee_id
            ORDER BY s.salary_month DESC
        """)

        self.assertEqual(result, [
            ("John Doe", "2024-05", 5000.75),
            ("Jane Smith", "2024-04", 4500.50)
        ])

    def test_get_employee_leaves(self):
        self.mock_cursor.fetchall.return_value = [
            ("Sick", 3),
            ("Vacation", 5)
        ]

        result = self.mysql.get_employee_leaves("123", "2024-05")

        self.mock_cursor.execute.assert_called_once_with(
            """
                    SELECT leave_type, duration
                    FROM Leaves
                    WHERE employee_id = %s AND start_date BETWEEN %s AND %s
                """,
            ("123", "2024-05-01", "2024-05-31")
        )

        self.assertEqual(result, [
            {'leave_type': "Sick", 'duration': 3},
            {'leave_type': "Vacation", 'duration': 5}
        ])

    def test_get_info_for_request(self):
        self.mock_cursor.fetchone.return_value = ("John Doe", "IT Academy", "johndoe@example.com")

        result = self.mysql.get_info_for_request("123")

        self.mock_cursor.execute.assert_called_once_with(
            """
            SELECT e.full_name, c.company_name, p.email
            FROM Employee e
            JOIN PersonalInfo p ON e.employee_id = p.employee_id
            JOIN Company c
            WHERE e.employee_id = %s
        """,
            ("123",)
        )

        self.assertEqual(result, {
            "full_name": "John Doe",
            "company_name": "IT Academy",
            "email": "johndoe@example.com"
        })

    def test_get_info_for_request_no_result(self):
        self.mock_cursor.fetchone.return_value = None

        result = self.mysql.get_info_for_request("123")

        self.assertIsNone(result)


    def test_get_employee_full_info(self):
        self.mock_cursor.fetchone.return_value = (
            "John Doe", "Finance", "Manager", "2023-04-27", 5,
            "1990-01-01", "Male", 2, "123456789", "Married", "johndoe@example.com"
        )

        result = self.mysql.get_employee_full_info("123")

        expected_query = """
            SELECT 
                e.full_name,
                d.department_name,
                p.position_name,
                g.hire_date,
                g.total_experience,
                pi.birth_date,
                pi.sex,
                pi.number_of_children,
                pi.phone_number,
                pi.marital_status,
                pi.email
            FROM Employee e
            JOIN GeneralInfo g ON e.employee_id = g.employee_id
            JOIN Departments d ON g.department_id = d.department_id
            JOIN Positions p ON g.position_id = p.position_id
            JOIN PersonalInfo pi ON e.employee_id = pi.employee_id
            WHERE e.employee_id = %s
        """

        actual_call = self.mock_cursor.execute.call_args[0][0]
        self.assertEqual(self.normalize_sql(actual_call), self.normalize_sql(expected_query))

        expected_result = {
            "full_name": "John Doe",
            "department_name": "Finance",
            "position_name": "Manager",
            "hire_date": "2023-04-27",
            "total_experience": 5,
            "birth_date": "1990-01-01",
            "sex": "Male",
            "number_of_children": 2,
            "phone_number": "123456789",
            "marital_status": "Married",
            "email": "johndoe@example.com"
        }
        self.assertEqual(result, expected_result)

    def test_get_employee_info_for_calculation_salary(self):
        self.mock_cursor.fetchone.return_value = ("John Doe", 5000.75, 5)

        result = self.mysql.get_employee_info_for_calculation_salary("123")

        expected_query = """
            SELECT E.full_name, P.salary_amount, GI.total_experience
            FROM Employee E
            JOIN GeneralInfo GI ON E.employee_id = GI.employee_id
            JOIN Positions P ON GI.position_id = P.position_id
            WHERE E.employee_id = %s
        """

        actual_call = self.mock_cursor.execute.call_args[0][0]
        self.assertEqual(self.normalize_sql(actual_call), self.normalize_sql(expected_query))

        expected_result = {
            'employee_id': "123",
            'full_name': "John Doe",
            'salary_amount': 5000.75,
            'total_experience': 5
        }
        self.assertEqual(result, expected_result)

    def test_get_salary_history(self):
        self.mock_cursor.fetchall.return_value = [
            {"salary_month": "2024-04", "salary_amount": 5000.75},
            {"salary_month": "2024-03", "salary_amount": 4500.50}
        ]

        result = self.mysql.get_salary_history("123")

        expected_query = """
            SELECT 
                salary_month, 
                salary_amount 
            FROM 
                Salary
            WHERE 
                employee_id = %s
            ORDER BY 
                salary_month DESC
        """

        actual_call = self.mock_cursor.execute.call_args[0][0]
        self.assertEqual(self.normalize_sql(actual_call), self.normalize_sql(expected_query))

        expected_result = [
            {"salary_month": "2024-04", "salary_amount": 5000.75},
            {"salary_month": "2024-03", "salary_amount": 4500.50}
        ]
        self.assertEqual(result, expected_result)

    def test_get_leaves_history(self):
        self.mock_cursor.fetchall.return_value = [
            {"leave_type": "Sick", "start_date": "2024-04-01", "end_date": "2024-04-05", "duration": 5},
            {"leave_type": "Vacation", "start_date": "2024-05-01", "end_date": "2024-05-10", "duration": 10}
        ]

        result = self.mysql.get_leaves_history("123")

        expected_query = """
            SELECT 
                leave_type,
                start_date,
                end_date,
                duration
            FROM 
                Leaves
            WHERE 
                employee_id = %s
        """

        actual_call = self.mock_cursor.execute.call_args[0][0]
        self.assertEqual(self.normalize_sql(actual_call), self.normalize_sql(expected_query))

        expected_result = [
            {"leave_type": "Sick", "start_date": "2024-04-01", "end_date": "2024-04-05", "duration": 5},
            {"leave_type": "Vacation", "start_date": "2024-05-01", "end_date": "2024-05-10", "duration": 10}
        ]
        self.assertEqual(result, expected_result)

    def test_get_retirement_age_employees(self):
        self.mock_cursor.fetchall.return_value = [
            {"employee_id": "123", "full_name": "John Doe", "age": 65, "experience": 40},
            {"employee_id": "124", "full_name": "Jane Smith", "age": 60, "experience": 35}
        ]

        result = self.mysql.get_retirement_age_employees()

        expected_query = """
            SELECT 
                e.employee_id,
                e.full_name,
                TIMESTAMPDIFF(YEAR, p.birth_date, CURDATE()) AS age,
                g.total_experience AS experience
            FROM 
                Employee e
            JOIN 
                PersonalInfo p ON e.employee_id = p.employee_id
            JOIN 
                GeneralInfo g ON e.employee_id = g.employee_id
            WHERE 
                TIMESTAMPDIFF(YEAR, p.birth_date, CURDATE()) >= 60;
        """

        actual_call = self.mock_cursor.execute.call_args[0][0]
        self.assertEqual(self.normalize_sql(actual_call), self.normalize_sql(expected_query))

        expected_result = [
            {"employee_id": "123", "full_name": "John Doe", "age": 65, "experience": 40},
            {"employee_id": "124", "full_name": "Jane Smith", "age": 60, "experience": 35}
        ]
        self.assertEqual(result, expected_result)

    def test_get_employees_below_average_salary(self):
        self.mock_cursor.fetchall.return_value = [
            {"department_name": "Finance", "average_salary": 5000.00, "full_name": "John Doe",
             "salary_amount": 4500.00},
            {"department_name": "IT", "average_salary": 6000.00, "full_name": "Jane Smith", "salary_amount": 5500.00}
        ]

        result = self.mysql.get_employees_below_average_salary()

        expected_query = """
            SELECT 
                d.department_name,
                d.average_salary, 
                e.full_name,
                p.salary_amount
            FROM 
                Employee e
            JOIN 
                GeneralInfo g ON e.employee_id = g.employee_id
            JOIN 
                Departments d ON g.department_id = d.department_id
            JOIN 
                Positions p ON g.position_id = p.position_id
            WHERE 
                p.salary_amount < d.average_salary;
        """

        actual_call = self.mock_cursor.execute.call_args[0][0]
        self.assertEqual(self.normalize_sql(actual_call), self.normalize_sql(expected_query))

        expected_result = [
            {"department_name": "Finance", "average_salary": 5000.00, "full_name": "John Doe",
             "salary_amount": 4500.00},
            {"department_name": "IT", "average_salary": 6000.00, "full_name": "Jane Smith", "salary_amount": 5500.00}
        ]
        self.assertEqual(result, expected_result)

    def test_get_average_age_by_department_and_company(self):
        self.mock_cursor.fetchall.return_value = [
            {"department_name": "Finance", "average_age": 35},
            {"department_name": "IT", "average_age": 29}
        ]

        self.mock_cursor.fetchone.return_value = {"average_age_company": 32}

        department_result, company_result = self.mysql.get_average_age_by_department_and_company()

        expected_department_query = """
            SELECT 
                d.department_name,
                ROUND(AVG(TIMESTAMPDIFF(YEAR, p.birth_date, CURDATE()))) AS average_age
            FROM 
                Employee e
            JOIN 
                PersonalInfo p ON e.employee_id = p.employee_id
            JOIN 
                GeneralInfo g ON e.employee_id = g.employee_id
            JOIN 
                Departments d ON g.department_id = d.department_id
            GROUP BY 
                d.department_name
        """

        expected_company_query = """
            SELECT 
                ROUND(AVG(TIMESTAMPDIFF(YEAR, p.birth_date, CURDATE()))) AS average_age_company
            FROM 
                PersonalInfo p
        """

        calls = [self.normalize_sql(call[0][0]) for call in self.mock_cursor.execute.call_args_list]
        self.assertIn(self.normalize_sql(expected_department_query), calls)
        self.assertIn(self.normalize_sql(expected_company_query), calls)

        expected_department_result = [
            {"department_name": "Finance", "average_age": 35},
            {"department_name": "IT", "average_age": 29}
        ]
        expected_company_result = {"average_age_company": 32}

        self.assertEqual(department_result, expected_department_result)
        self.assertEqual(company_result, expected_company_result)

    def test_get_sick_leave_duration_by_department(self):
        self.mock_cursor.fetchall.side_effect = [
            [{"department_name": "Finance", "total_leave_duration": 15},
             {"department_name": "IT", "total_leave_duration": 10}],
            [{"department_name": "Finance", "leave_month": 3, "total_leave_duration": 5},
             {"department_name": "IT", "leave_month": 4, "total_leave_duration": 10}]
        ]

        total_result, monthly_result = self.mysql.get_sick_leave_duration_by_department()

        expected_total_query = """
            SELECT 
                d.department_name,
                SUM(l.duration) AS total_leave_duration
            FROM 
                Leaves l
            JOIN 
                GeneralInfo g ON l.employee_id = g.employee_id
            JOIN 
                Departments d ON g.department_id = d.department_id
            WHERE 
                l.leave_type = 'Sick'
            GROUP BY 
                d.department_name
        """

        expected_monthly_query = """
            SELECT 
                d.department_name,
                MONTH(l.start_date) AS leave_month,
                SUM(l.duration) AS total_leave_duration
            FROM 
                Leaves l
            JOIN 
                GeneralInfo g ON l.employee_id = g.employee_id
            JOIN 
                Departments d ON g.department_id = d.department_id
            WHERE 
                l.leave_type = 'Sick'
            GROUP BY 
                d.department_name, leave_month
        """

        calls = [self.normalize_sql(call[0][0]) for call in self.mock_cursor.execute.call_args_list]
        self.assertIn(self.normalize_sql(expected_total_query), calls)
        self.assertIn(self.normalize_sql(expected_monthly_query), calls)

        expected_total_result = [
            {"department_name": "Finance", "total_leave_duration": 15},
            {"department_name": "IT", "total_leave_duration": 10}
        ]

        expected_monthly_result = [
            {"department_name": "Finance", "leave_month": 3, "total_leave_duration": 5},
            {"department_name": "IT", "leave_month": 4, "total_leave_duration": 10}
        ]

        self.assertEqual(total_result, expected_total_result)
        self.assertEqual(monthly_result, expected_monthly_result)

    def test_get_average_experience_by_department(self):
        self.mock_cursor.fetchall.return_value = [
            {"department_name": "Finance", "average_experience": 7.5},
            {"department_name": "IT", "average_experience": 5.2}
        ]

        result = self.mysql.get_average_experience_by_department()

        expected_query = """
            SELECT 
                d.department_name,
                ROUND(AVG(g.total_experience), 2) AS average_experience
            FROM 
                GeneralInfo g
            JOIN 
                Departments d ON g.department_id = d.department_id
            GROUP BY 
                d.department_name
        """

        actual_call = self.mock_cursor.execute.call_args[0][0]
        self.assertEqual(self.normalize_sql(actual_call), self.normalize_sql(expected_query))

        expected_result = [
            {"department_name": "Finance", "average_experience": 7.5},
            {"department_name": "IT", "average_experience": 5.2}
        ]
        self.assertEqual(result, expected_result)

    def test_get_average_earnings_by_gender_and_department(self):
        self.mock_cursor.fetchall.side_effect = [
            [
                {"department_name": "Finance", "sex": "Male", "average_salary": 5000.50},
                {"department_name": "Finance", "sex": "Female", "average_salary": 4800.00},
                {"department_name": "IT", "sex": "Male", "average_salary": 6000.00},
                {"department_name": "IT", "sex": "Female", "average_salary": 5700.75},
            ],
            [
                {"sex": "Male", "average_salary_company": 5500.25},
                {"sex": "Female", "average_salary_company": 5300.00},
            ]
        ]

        department_result, company_result = self.mysql.get_average_earnings_by_gender_and_department()

        expected_department_query = """
            SELECT 
                d.department_name,
                p.sex,
                ROUND(AVG(s.salary_amount), 2) AS average_salary
            FROM 
                Employee e
            JOIN 
                PersonalInfo p ON e.employee_id = p.employee_id
            JOIN 
                GeneralInfo g ON e.employee_id = g.employee_id
            JOIN 
                Departments d ON g.department_id = d.department_id
            JOIN 
                Salary s ON e.employee_id = s.employee_id
            GROUP BY 
                d.department_name, p.sex
        """

        expected_company_query = """
            SELECT 
                p.sex,
                ROUND(AVG(s.salary_amount), 2) AS average_salary_company
            FROM 
                Employee e
            JOIN 
                PersonalInfo p ON e.employee_id = p.employee_id
            JOIN 
                Salary s ON e.employee_id = s.employee_id
            GROUP BY 
                p.sex
        """

        calls = [self.normalize_sql(call[0][0]) for call in self.mock_cursor.execute.call_args_list]
        self.assertIn(self.normalize_sql(expected_department_query), calls)
        self.assertIn(self.normalize_sql(expected_company_query), calls)

        expected_department_result = [
            {"department_name": "Finance", "sex": "Male", "average_salary": 5000.50},
            {"department_name": "Finance", "sex": "Female", "average_salary": 4800.00},
            {"department_name": "IT", "sex": "Male", "average_salary": 6000.00},
            {"department_name": "IT", "sex": "Female", "average_salary": 5700.75},
        ]

        expected_company_result = [
            {"sex": "Male", "average_salary_company": 5500.25},
            {"sex": "Female", "average_salary_company": 5300.00},
        ]

        self.assertEqual(department_result, expected_department_result)
        self.assertEqual(company_result, expected_company_result)

    def test_get_departments(self):
        self.mock_cursor.fetchall.return_value = [
            (1, "Finance"),
            (2, "IT"),
            (3, "HR")
        ]

        result = self.mysql.get_departments()

        expected_query = "SELECT department_id, department_name FROM Departments"

        self.mock_cursor.execute.assert_called_once_with(expected_query)

        expected_result = [
            (1, "Finance"),
            (2, "IT"),
            (3, "HR")
        ]
        self.assertEqual(result, expected_result)

    def test_get_positions(self):
        self.mock_cursor.fetchall.return_value = [
            (1, "Manager"),
            (2, "Developer"),
            (3, "HR Specialist")
        ]

        department_id = 2
        result = self.mysql.get_positions(department_id)

        expected_query = """
            SELECT position_id, position_name
            FROM Positions
            WHERE department_id = %s
        """

        self.mock_cursor.execute.assert_called_once_with(expected_query, (department_id,))

        expected_result = [
            (1, "Manager"),
            (2, "Developer"),
            (3, "HR Specialist")
        ]
        self.assertEqual(result, expected_result)

    def test_check_user_email(self):
        self.mock_cursor.fetchone.return_value = ("john.doe@example.com",)

        worker_id = "123"
        result = self.mysql.check_user_email(worker_id)

        expected_query = "SELECT email FROM PersonalInfo WHERE employee_id = %s"

        self.mock_cursor.execute.assert_called_once_with(expected_query, (worker_id,))

        self.assertEqual(result, "john.doe@example.com")

    def test_check_user_email_no_result(self):
        self.mock_cursor.fetchone.return_value = None

        worker_id = "123"
        result = self.mysql.check_user_email(worker_id)

        expected_query = "SELECT email FROM PersonalInfo WHERE employee_id = %s"

        self.mock_cursor.execute.assert_called_once_with(expected_query, (worker_id,))

        self.assertIsNone(result)

    @patch('builtins.open', new_callable=mock_open, read_data=json.dumps({
        "departments": [
            {
                "name": "Finance",
                "positions": [
                    {"name": "Manager", "salary": 5000},
                    {"name": "Analyst", "salary": 4000}
                ]
            },
            {
                "name": "IT",
                "positions": [
                    {"name": "Developer", "salary": 6000},
                    {"name": "DevOps", "salary": 5500}
                ]
            }
        ]
    }))

    def test_check_and_insert_departments(self, mock_file):
        self.mock_cursor.fetchone.return_value = (0,)

        self.mysql.check_and_insert_departments()

        expected_calls = [
            call("SELECT COUNT(*) FROM Company"),
            call("INSERT INTO Company (company_name, num_of_departments) VALUES (%s, %s)", ("IT Academy", 2)),
            call("INSERT INTO Departments (department_name, department_positions, average_salary) VALUES (%s, %s, %s)",
                 ("Finance", 2, 4500.0)),
            call("INSERT INTO Positions (department_id, position_name, salary_amount) VALUES (%s, %s, %s)",
                 (self.mock_cursor.lastrowid, "Manager", 5000)),
            call("INSERT INTO Positions (department_id, position_name, salary_amount) VALUES (%s, %s, %s)",
                 (self.mock_cursor.lastrowid, "Analyst", 4000)),
            call("INSERT INTO Departments (department_name, department_positions, average_salary) VALUES (%s, %s, %s)",
                 ("IT", 2, 5750.0)),
            call("INSERT INTO Positions (department_id, position_name, salary_amount) VALUES (%s, %s, %s)",
                 (self.mock_cursor.lastrowid, "Developer", 6000)),
            call("INSERT INTO Positions (department_id, position_name, salary_amount) VALUES (%s, %s, %s)",
                 (self.mock_cursor.lastrowid, "DevOps", 5500))
        ]

        self.mock_cursor.execute.assert_has_calls(expected_calls, any_order=False)

        self.mock_connection.commit.assert_called_once()

        mock_file.assert_called_once_with('databases/departments.json', 'r')

    def test_create_trigger_calculate_experience_generalinfo(self):
        expected_insert_trigger = self.normalize_sql("""
            CREATE TRIGGER calculate_experience_generalinfo_before_insert
            BEFORE INSERT ON GeneralInfo
            FOR EACH ROW
            BEGIN
                SET NEW.total_experience = NEW.previous_experience + YEAR(CURDATE()) - YEAR(NEW.hire_date);
            END;
        """)

        expected_update_trigger = self.normalize_sql("""
            CREATE TRIGGER calculate_experience_generalinfo_before_update
            BEFORE UPDATE ON GeneralInfo
            FOR EACH ROW
            BEGIN
                SET NEW.total_experience = NEW.previous_experience + YEAR(CURDATE()) - YEAR(NEW.hire_date);
            END;
        """)

        with patch('builtins.print') as mock_print:
            self.mysql.create_trigger_calculate_experience_generalinfo()

        actual_calls = [self.normalize_sql(call.args[0]) for call in self.mock_cursor.execute.call_args_list]

        self.assertIn(expected_insert_trigger, actual_calls)
        self.assertIn(expected_update_trigger, actual_calls)

        mock_print.assert_any_call("Trigger 'calculate_experience_generalinfo_before_insert' is successfully created.")
        mock_print.assert_any_call("Trigger 'calculate_experience_generalinfo_before_update' is successfully created.")

    def test_create_update_duration_trigger(self):
        expected_trigger_query = self.normalize_sql("""
            CREATE TRIGGER IF NOT EXISTS update_duration_on_update
            BEFORE UPDATE ON Leaves
            FOR EACH ROW
            BEGIN
                SET NEW.duration = DATEDIFF(NEW.end_date, NEW.start_date) + 1;
            END;
        """)

        with patch('builtins.print') as mock_print:
            self.mysql.create_update_duration_trigger()

        actual_call = self.normalize_sql(self.mock_cursor.execute.call_args[0][0])

        self.assertEqual(expected_trigger_query, actual_call)

        mock_print.assert_called_once_with("Trigger 'update_duration_on_update' created successfully.")

    def test_create_trigger_calculate_experience_generalinfo_error(self):
        self.mock_cursor.execute.side_effect = mysql.connector.Error("Trigger already exists")

        with patch('builtins.print') as mock_print:
            self.mysql.create_trigger_calculate_experience_generalinfo()

        self.assertEqual(self.mock_cursor.execute.call_count, 2)

        mock_print.assert_any_call("Trigger 'calculate_experience_generalinfo_before_insert' already exists.")
        mock_print.assert_any_call("Trigger 'calculate_experience_generalinfo_before_update' already exists.")

    def test_create_update_duration_trigger_error(self):
        self.mock_cursor.execute.side_effect = Exception("Some error occurred")

        with patch('builtins.print') as mock_print:
            self.mysql.create_update_duration_trigger()

        self.mock_connection.rollback.assert_called_once()

        mock_print.assert_called_once_with("Error creating trigger: Some error occurred")

if __name__ == '__main__':
    unittest.main()