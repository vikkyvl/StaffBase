import unittest
from unittest.mock import MagicMock, patch
from PyQt5.QtWidgets import QApplication, QMessageBox
from design.auth_pages_main import MainPage
import sys

app = QApplication(sys.argv)

class TestMainPage(unittest.TestCase):
    def setUp(self):
        with patch('design.auth_pages_main.MySQL') as MockMySQL:
            self.mock_mysql = MockMySQL.return_value
            self.main_page = MainPage()
            self.main_page.redis_connection = MagicMock()
            self.main_page.auth_process = MagicMock()

    def test_switch_page(self):
        self.main_page.switch_page(2)
        self.assertEqual(self.main_page.ui.stackedWidget.currentIndex(), 2)

    def test_admin_auth_page_correct_password(self):
        self.main_page.redis_connection.get_admin_password.return_value = "correct_password"
        self.main_page.ui.admin_password_lineEdit.setText("correct_password")

        with patch.object(self.main_page, 'open_admin_page') as mock_open_admin_page:
            self.main_page.admin_auth_page()
            mock_open_admin_page.assert_called_once()

    def test_admin_auth_page_incorrect_password(self):
        self.main_page.redis_connection.get_admin_password.return_value = "correct_password"
        self.main_page.ui.admin_password_lineEdit.setText("wrong_password")

        with patch.object(QMessageBox, 'warning') as mock_warning:
            self.main_page.admin_auth_page()
            mock_warning.assert_called_once_with(
                self.main_page,
                "Error",
                "Incorrect password. Please try again or click 'Forgot your password'."
            )

    def test_user_auth_page_existing_user_correct_password(self):
        self.main_page.redis_connection.is_exist_user.return_value = 1
        self.main_page.redis_connection.get_password_by_login.return_value = "correct_password"
        self.main_page.redis_connection.get_id_by_login.return_value = 1

        self.main_page.ui.user_login_lineEdit.setText("user_login")
        self.main_page.ui.user_password_lineEdit.setText("correct_password")

        with patch.object(self.main_page, 'open_user_page') as mock_open_user_page:
            self.main_page.user_auth_page()
            mock_open_user_page.assert_called_once_with(1)

    def test_user_auth_page_user_not_found(self):
        self.main_page.redis_connection.is_exist_user.return_value = 0

        self.main_page.ui.user_login_lineEdit.setText("non_existing_user")

        with patch.object(QMessageBox, 'warning') as mock_warning:
            self.main_page.user_auth_page()
            mock_warning.assert_called_once_with(
                self.main_page,
                "Error",
                "This user does not exist. Please contact the administrator or check the login you entered."
            )

    def test_clear_line_edits(self):
        line_edits = [
            self.main_page.ui.first_n_lineEdit,
            self.main_page.ui.second_n_lineEdit,
            self.main_page.ui.third_n_lineEdit
        ]
        for line_edit in line_edits:
            line_edit.setText("123")

        self.main_page.clear_line_edits(line_edits)

        for line_edit in line_edits:
            self.assertEqual(line_edit.text(), "")

if __name__ == '__main__':
    unittest.main()
