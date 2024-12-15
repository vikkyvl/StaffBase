import unittest
from unittest.mock import MagicMock, patch
from classes.employee import Employee
from classes.general_info import GeneralInfo
from classes.personal_info import PersonalInfo
from databases.mysqlDB import MySQL
from datetime import date

class TestMySQL(unittest.TestCase):

    def setUp(self):
        # Створюємо мок для MySQL класу
        self.mysql = MySQL()
        self.mysql.cursor = MagicMock()
        self.mysql.mydb = MagicMock()

    @patch('databases.mysqlDB.mysql.connector.connect')
    def test_connection(self, mock_connect):
        MySQL()
        mock_connect.assert_called_once()

    def test_add_employee(self):
        employee = Employee("123", "John Doe")

        self.mysql.add_employee(employee)

        self.mysql.cursor.execute.assert_called_once_with(
            "INSERT INTO Employee (employee_id, full_name) VALUES (%s, %s)",
            ("123", "John Doe")
        )
        self.mysql.mydb.commit.assert_called_once()
        self.mysql.cursor.close.assert_called_once()

    def test_add_general_info(self):
        general_info = GeneralInfo(
            employee_id="123",
            department_id=1,
            position_id=2,
            hire_date=date(2024, 4, 27),
            experience=5
        )

        self.mysql.add_general_info(general_info)

        self.mysql.cursor.execute.assert_called_once_with(
            """INSERT INTO GeneralInfo (employee_id, department_id, position_id, hire_date, experience)
               VALUES (%s, %s, %s, %s, %s)""",
            ("123", 1, 2, date(2024, 4, 27), 5)
        )
        self.mysql.mydb.commit.assert_called_once()
        self.mysql.cursor.close.assert_called_once()

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

        self.mysql.cursor.execute.assert_called_once_with(
            """INSERT INTO PersonalInfo (employee_id, birth_date, sex, number_of_children, phone_number, marital_status, email)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            ("123", date(1990, 1, 1), "Male", 2, "1234567890", "Married", "johndoe@example.com")
        )
        self.mysql.mydb.commit.assert_called_once()
        self.mysql.cursor.close.assert_called_once()

    def test_get_email_by_id(self):
        self.mysql.cursor.fetchone.return_value = ("johndoe@example.com",)

        result = self.mysql.get_email_by_id("123")
        self.assertEqual(result, "johndoe@example.com")

        self.mysql.cursor.execute.assert_called_once_with(
            "SELECT email FROM PersonalInfo WHERE employee_id = %s",
            ("123",)
        )

    def test_check_and_insert_departments(self):
        mock_json_data = {
            "departments": [
                {
                    "name": "HR",
                    "positions": [
                        {"name": "Manager", "salary": 5000},
                        {"name": "Assistant", "salary": 3000}
                    ]
                }
            ]
        }

        with patch('builtins.open', unittest.mock.mock_open(read_data='{"departments": [{"name": "HR", "positions": [{"name": "Manager", "salary": 5000}, {"name": "Assistant", "salary": 3000}]}]}')), \
             patch('json.load', return_value=mock_json_data):

            self.mysql.cursor.fetchone.return_value = (0,)

            self.mysql.check_and_insert_departments()

            self.mysql.cursor.execute.assert_any_call(
                "INSERT INTO Departments (department_name, department_positions) VALUES (%s, %s)",
                ("HR", 2)
            )

            self.mysql.mydb.commit.assert_called_once()

if __name__ == '__main__':
    unittest.main()
