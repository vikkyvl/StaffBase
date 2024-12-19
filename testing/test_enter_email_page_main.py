import unittest
from unittest.mock import MagicMock, patch
from PyQt5 import QtWidgets, QtCore
from design.enter_email_page_main import EnterEmailPage


class TestEnterEmailPage(unittest.TestCase):
    @patch('design.enter_email_page_main.QtWidgets.QMessageBox')
    @patch('design.enter_email_page_main.EnterEmailPage.show')
    def setUp(self, mock_show, mock_messagebox):
        self.app = QtWidgets.QApplication([])
        self.mock_mysql = MagicMock()
        self.worker_id = "123"

        self.enter_email_page = EnterEmailPage(mysql_connection=self.mock_mysql, worker_id=self.worker_id)

    def tearDown(self):
        self.app.quit()

    def test_invalid_email_shows_warning(self):
        self.enter_email_page.ui.lineEdit.setText("invalid-email")

        with patch.object(QtWidgets.QMessageBox, 'warning') as mock_warning:
            self.enter_email_page.read_and_validate_email()
            mock_warning.assert_called_once_with(
                self.enter_email_page, "Invalid Email", "Please enter a valid email address."
            )

    def test_valid_email_updates_successfully(self):
        self.enter_email_page.ui.lineEdit.setText("test@example.com")

        with patch.object(QtWidgets.QMessageBox, 'information') as mock_info:
            self.enter_email_page.read_and_validate_email()
            self.mock_mysql.update_user_email.assert_called_once_with(self.worker_id, "test@example.com")
            mock_info.assert_called_once_with(
                self.enter_email_page, "Success", "Email updated successfully!"
            )

    def test_update_email_failure_shows_error(self):
        self.enter_email_page.ui.lineEdit.setText("test@example.com")
        self.mock_mysql.update_user_email.side_effect = Exception("Database error")

        with patch.object(QtWidgets.QMessageBox, 'critical') as mock_critical:
            self.enter_email_page.read_and_validate_email()
            mock_critical.assert_called_once_with(
                self.enter_email_page, "Error", "Failed to update email: Database error"
            )

if __name__ == '__main__':
    unittest.main()
