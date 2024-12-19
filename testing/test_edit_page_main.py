import unittest
from unittest.mock import MagicMock, patch
from PyQt5 import QtWidgets
from design.edit_page.edit_page_main import EditPage

class TestEditPage(unittest.TestCase):
    @patch('design.edit_page.edit_page_main.Redis')
    @patch('design.edit_page.edit_page_main.MySQL')
    @patch('design.edit_page.edit_page_main.QtWidgets.QDialog.exec_', return_value=None)
    def setUp(self, mock_exec, mock_mysql, mock_redis):
        if not QtWidgets.QApplication.instance():
            self.app = QtWidgets.QApplication([])
        else:
            self.app = QtWidgets.QApplication.instance()

        self.mock_redis = mock_redis.return_value
        self.mock_mysql = mock_mysql.return_value

        self.worker_table = MagicMock()
        self.mock_model = MagicMock()
        self.worker_table.model.return_value = self.mock_model
        self.worker_table.currentIndex.return_value.row.return_value = 0

        self.mock_model.index.return_value.data.return_value = "test_value"

        with patch.object(EditPage, 'fill_fields_from_table'):
            self.edit_page = EditPage(self.mock_redis, self.mock_mysql, worker_table=self.worker_table)

    def tearDown(self):
        self.app.quit()

    def test_validate_input_invalid_login(self):
        invalid_login = "johndoe"
        valid_password = "Password123!"
        valid_full_name = "John Doe"
        valid_experience = "5"

        with patch.object(self.edit_page, 'show_critical_message') as mock_critical_message:
            result = self.edit_page.validate_input(invalid_login, valid_password, valid_full_name, valid_experience)

            self.assertFalse(result)
            mock_critical_message.assert_called_once_with("Error", "Login must be in the format 'name_username'.")

    def test_validate_input_invalid_password(self):
        valid_login = "john_doe"
        invalid_password = "password"
        valid_full_name = "John Doe"
        valid_experience = "5"

        with patch.object(self.edit_page, 'show_critical_message') as mock_critical_message:
            result = self.edit_page.validate_input(valid_login, invalid_password, valid_full_name, valid_experience)

            self.assertFalse(result)
            mock_critical_message.assert_called_once_with("Error",
                                                          "Password must contain letters, digits, and symbols.")

    def test_validate_input_invalid_full_name(self):
        valid_login = "john_doe"
        valid_password = "Password123!"
        invalid_full_name = "john doe"
        valid_experience = "5"

        with patch.object(self.edit_page, 'show_critical_message') as mock_critical_message:
            result = self.edit_page.validate_input(valid_login, valid_password, invalid_full_name, valid_experience)

            self.assertFalse(result)
            mock_critical_message.assert_called_once_with("Error",
                                                          "Full Name must consist of two words starting with uppercase letters.")

    def test_validate_input_invalid_experience(self):
        valid_login = "john_doe"
        valid_password = "Password123!"
        valid_full_name = "John Doe"
        invalid_experience = "invalid"

        with patch.object(self.edit_page, 'show_critical_message') as mock_critical_message:
            result = self.edit_page.validate_input(valid_login, valid_password, valid_full_name, invalid_experience)

            self.assertFalse(result)
            mock_critical_message.assert_called_once_with("Error", "Experience must be a number between 0 and 70.")

    def test_update_employee_data_success(self):
        self.worker_table.currentIndex.return_value.row.return_value = 0
        self.mock_model = self.worker_table.model.return_value
        self.mock_model.index.side_effect = lambda row, col: MagicMock(data=lambda: f"value_{col}")

        self.edit_page.ui.login_lineEdit.setText("john_willson")
        self.edit_page.ui.password_lineEdit.setText("NewPassword123!")
        self.edit_page.ui.full_name_lineEdit.setText("John Willson")
        self.edit_page.ui.experience_lineEdit.setText("5")

        self.mock_redis.update_employee_login.return_value = True
        self.mock_redis.update_employee_password.return_value = True
        self.mock_mysql.update_employee.return_value = True

        with patch.object(self.edit_page, 'show_success_message') as mock_info:
            self.edit_page.update_employee_data()
            mock_info.assert_called_once_with("Success", "Employee data updated successfully!")

    def test_update_employee_data_failed_update(self):
        self.edit_page.ui.login_lineEdit.setText("john_doe")
        self.edit_page.ui.password_lineEdit.setText("Password123!")
        self.edit_page.ui.full_name_lineEdit.setText("John Doe")
        self.edit_page.ui.experience_lineEdit.setText("5")

        self.mock_redis.update_employee_login.return_value = True
        self.mock_redis.update_employee_password.return_value = True
        self.mock_mysql.update_employee.return_value = False

        with patch.object(QtWidgets.QMessageBox, 'critical') as mock_critical:
            self.edit_page.update_employee_data()
            mock_critical.assert_called_once_with(self.edit_page.edit_page, "Error", "Failed to update employee data.")

if __name__ == '__main__':
    unittest.main()
