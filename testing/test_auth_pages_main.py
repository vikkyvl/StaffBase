import unittest
from unittest.mock import MagicMock, patch
from PyQt5 import QtWidgets
from design.auth_pages_main import MainPage


class TestMainPage(unittest.TestCase):
    @patch('design.auth_pages_main.Redis')
    @patch('design.auth_pages_main.MySQL')
    def setUp(self, mock_redis_class, mock_mysql_class):
        self.app = QtWidgets.QApplication([])

        self.mock_redis = mock_redis_class.return_value
        self.mock_mysql = mock_mysql_class.return_value

        self.main_page = MainPage()

    def tearDown(self):
        self.app.quit()

    @patch.object(MainPage, 'open_admin_page')
    def test_admin_auth_page_correct_password(self, mock_open_admin_page):
        self.mock_redis.get_admin_password.return_value = "1235"

        self.main_page.ui.admin_password_lineEdit.setText("1235")

        self.main_page.admin_auth_page()

        mock_open_admin_page.assert_called_once()

    @patch.object(QtWidgets.QMessageBox, 'warning')
    def test_admin_auth_page_incorrect_password(self, mock_warning):
        self.mock_redis.get_admin_password.return_value = "1235"

        self.main_page.ui.admin_password_lineEdit.setText("wrong_password")

        self.main_page.admin_auth_page()

        mock_warning.assert_called_once_with(
            self.main_page, "Error", "Incorrect password. Please try again or click 'Forgot your password'."
        )

        self.assertEqual(self.main_page.ui.admin_password_lineEdit.text(), "")


if __name__ == '__main__':
    unittest.main()
