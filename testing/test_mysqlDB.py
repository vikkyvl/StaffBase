# import unittest
# from unittest.mock import MagicMock, patch, mock_open
# from classes.employee import Employee
# from classes.general_info import GeneralInfo
# from classes.personal_info import PersonalInfo
# from databases.mysqlDB import MySQL
# from datetime import date
#
# class TestMySQL(unittest.TestCase):
#
#     @patch('databases.mysqlDB.mysql.connector.connect')
#     def setUp(self, mock_connect):
#         self.mock_connection = MagicMock()
#         mock_connect.return_value = self.mock_connection
#
#         self.mock_cursor = MagicMock()
#         self.mock_connection.cursor.return_value = self.mock_cursor
#
#         with patch.object(MySQL, 'create_tables'), \
#                 patch.object(MySQL, 'check_and_insert_departments'), \
#                 patch.object(MySQL, 'create_trigger_calculate_experience_generalinfo'):
#             self.mysql = MySQL()
#
#     def test_add_employee(self):
#         employee = Employee("123", "John Doe")
#
#         self.mysql.add_employee(employee)
#
#         self.mock_cursor.execute.assert_called_once_with(
#             "INSERT INTO Employee (employee_id, full_name) VALUES (%s, %s)",
#             ("123", "John Doe")
#         )
#         self.mock_connection.commit.assert_called_once()
#         self.mock_cursor.close.assert_called_once()
#
#     def test_add_general_info(self):
#         general_info = GeneralInfo(
#             employee_id="123",
#             department_id=1,
#             position_id=2,
#             hire_date=date(2024, 4, 27),
#             experience=5
#         )
#
#         self.mysql.add_general_info(general_info)
#
#         self.mock_cursor.execute.assert_any_call(
#             unittest.mock.ANY,
#             ("123", 1, 2, date(2024, 4, 27), 5)
#         )
#         self.mock_connection.commit.assert_called_once()
#         self.mock_cursor.close.assert_called_once()
#
#     def test_add_personal_info(self):
#         personal_info = PersonalInfo(
#             employee_id="123",
#             birth_date=date(1990, 1, 1),
#             sex="Male",
#             number_of_children=2,
#             phone_number="1234567890",
#             marital_status="Married",
#             email="johndoe@example.com"
#         )
#
#         self.mysql.add_personal_info(personal_info)
#
#         self.mock_cursor.execute.assert_any_call(
#             unittest.mock.ANY,
#             ("123", date(1990, 1, 1), "Male", 2, "1234567890", "Married", "johndoe@example.com")
#         )
#         self.mock_connection.commit.assert_called_once()
#         self.mock_cursor.close.assert_called_once()
#
#     def test_get_worker_details(self):
#         self.mysql.get_worker_details("123")
#
#         self.mock_cursor.execute.assert_any_call(
#             unittest.mock.ANY,
#             ("123",)
#         )
#
#     def test_delete_worker_by_id(self):
#         self.mysql.delete_worker_by_id("123")
#
#         self.mysql.cursor.execute.assert_called_once_with(
#             "DELETE FROM Employee WHERE employee_id = %s",
#             ("123",)
#         )
#         self.mysql.mydb.commit.assert_called_once()
#
#
# if __name__ == '__main__':
#     unittest.main()
