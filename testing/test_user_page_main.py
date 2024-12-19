import unittest
from unittest.mock import MagicMock, patch
from PyQt5.QtWidgets import QApplication
from design.user_page_main import UserPage

import sys

class TestUserPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)

    @classmethod
    def tearDownClass(cls):
        cls.app.quit()

    def setUp(self):
        self.redis_mock = MagicMock()
        self.mysql_mock = MagicMock()

        self.worker_id = "123"

        self.mysql_mock.get_employee_full_info.return_value = {
            'full_name': 'John Doe',
            'department_name': 'IT Department',
            'position_name': 'Developer',
            'hire_date': '2020-01-01',
            'total_experience': 5,
            'birth_date': '1990-01-01',
            'sex': 'Male',
            'number_of_children': 2,
            'phone_number': '123456789',
            'marital_status': 'Married',
            'email': 'johndoe@example.com'
        }

        self.user_page = UserPage(redis_connection=self.redis_mock, mysql_connection=self.mysql_mock,
                                  worker_id=self.worker_id)

    def test_load_worker_info(self):
        self.mysql_mock.get_employee_full_info.return_value = {
            'full_name': 'John Doe',
            'department_name': 'IT Department',
            'position_name': 'Developer',
            'hire_date': '2020-01-01',
            'total_experience': 5,
            'birth_date': '1990-01-01',
            'sex': 'Male',
            'number_of_children': 2,
            'phone_number': '123456789',
            'marital_status': 'Married',
            'email': 'johndoe@example.com'
        }

        self.user_page.load_worker_info()

        self.mysql_mock.get_employee_full_info.assert_called_with(self.worker_id)

        self.assertEqual(self.user_page.ui.user_full_name_textEdit.toPlainText(), 'John Doe')

    def test_load_salary_history(self):
        self.mysql_mock.get_salary_history.return_value = [
            {"salary_month": "2024-01", "salary_amount": 1200.50},
            {"salary_month": "2024-02", "salary_amount": 1300.75}
        ]

        self.user_page.load_salary_history()

        self.mysql_mock.get_salary_history.assert_called_with(self.worker_id)

        model = self.user_page.ui.salary_history_tableView.model()
        self.assertEqual(model.rowCount(), 2)

    def test_load_leave_history(self):
        self.mysql_mock.get_leaves_history.return_value = [
            {"leave_type": "Vacation", "start_date": "2024-03-01", "end_date": "2024-03-10", "duration": 10},
            {"leave_type": "Sick", "start_date": "2024-04-01", "end_date": "2024-04-05", "duration": 5}
        ]

        self.user_page.load_leave_history()

        self.mysql_mock.get_leaves_history.assert_called_with(self.worker_id)

        model = self.user_page.ui.leave_history_tableView.model()
        self.assertEqual(model.rowCount(), 2)

    @patch('classes.authorization.Authorization.send_leave_request_email')
    def test_send_request_leave(self, mock_send_email):
        self.user_page.leave_data = ('John Doe', 'Vacation', 'Test email body')

        self.user_page.send_request_leave(*self.user_page.leave_data)

        mock_send_email.assert_called_with('John Doe', 'Vacation', 'Test email body')

if __name__ == '__main__':
    unittest.main()
