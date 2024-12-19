import unittest
from unittest.mock import MagicMock, patch
from PyQt5 import QtWidgets, QtCore
from design.add_page.add_page_main import AddPage

class TestAddPage(unittest.TestCase):
    @patch('design.add_page.add_page_main.Redis')
    @patch('design.add_page.add_page_main.MySQL')
    @patch('design.add_page.add_page_main.QtWidgets.QDialog.exec_', return_value=None)
    def setUp(self, mock_exec, mock_mysql, mock_redis):
        self.app = QtWidgets.QApplication([])

        self.mock_redis = mock_redis.return_value
        self.mock_mysql = mock_mysql.return_value

        self.add_page = AddPage(self.mock_redis, self.mock_mysql)

    def tearDown(self):
        self.app.quit()

    def test_validate_input_invalid_login(self):
        invalid_login = "johndoe"
        valid_password = "Password123!"
        valid_full_name = "John Doe"
        valid_experience = "5"

        with patch.object(self.add_page, 'show_critical_message') as mock_critical_message:
            result = self.add_page.validate_input(invalid_login, valid_password, valid_full_name, valid_experience)

            self.assertFalse(result)
            mock_critical_message.assert_called_once_with("Error", "Login must be in the format 'name_username'.")

    def test_validate_input_invalid_password(self):
        valid_login = "john_doe"
        invalid_password = "password"
        valid_full_name = "John Doe"
        valid_experience = "5"

        with patch.object(self.add_page, 'show_critical_message') as mock_critical_message:
            result = self.add_page.validate_input(valid_login, invalid_password, valid_full_name, valid_experience)

            self.assertFalse(result)
            mock_critical_message.assert_called_once_with("Error",
                                                          "Password must contain letters, digits, and symbols.")

    def test_validate_input_invalid_full_name(self):
        valid_login = "john_doe"
        valid_password = "Password123!"
        invalid_full_name = "john doe"
        valid_experience = "5"

        with patch.object(self.add_page, 'show_critical_message') as mock_critical_message:
            result = self.add_page.validate_input(valid_login, valid_password, invalid_full_name, valid_experience)

            self.assertFalse(result)
            mock_critical_message.assert_called_once_with("Error",
                                                          "Full Name must consist of two words starting with uppercase letters.")

    def test_validate_input_invalid_experience(self):
        valid_login = "john_doe"
        valid_password = "Password123!"
        valid_full_name = "John Doe"
        invalid_experience = "invalid"

        with patch.object(self.add_page, 'show_critical_message') as mock_critical_message:
            result = self.add_page.validate_input(valid_login, valid_password, valid_full_name, invalid_experience)

            self.assertFalse(result)
            mock_critical_message.assert_called_once_with("Error", "Experience must be a number between 0 and 70.")

    def test_add_date_success(self):
        self.add_page.ui.login_lineEdit.setText("john_doe")
        self.add_page.ui.password_lineEdit.setText("Password123!")
        self.add_page.ui.full_name_lineEdit.setText("John Doe")
        self.add_page.ui.sex_comboBox.addItem("Male")
        self.add_page.ui.sex_comboBox.setCurrentText("Male")
        self.add_page.ui.department_comboBox.addItem("Finance", 1)
        self.add_page.ui.department_comboBox.setCurrentIndex(0)
        self.add_page.ui.position_comboBox.addItem("Assistant", 2)
        self.add_page.ui.position_comboBox.setCurrentIndex(0)
        self.add_page.ui.hire_date_dateEdit.setDate(QtCore.QDate(2024, 4, 27))
        self.add_page.ui.experience_lineEdit.setText("5")
        self.add_page.ui.birth_date_dateEdit.setDate(QtCore.QDate(1990, 1, 1))

        self.mock_redis.add_employee = MagicMock()
        self.mock_mysql.add_employee = MagicMock()
        self.mock_mysql.add_personal_info = MagicMock()
        self.mock_mysql.add_general_info = MagicMock()

        with patch('design.add_page.add_page_main.QtWidgets.QMessageBox.information') as mock_info:
            self.add_page.add_date()

            self.mock_redis.add_employee.assert_called_once()
            self.mock_mysql.add_employee.assert_called_once()
            self.mock_mysql.add_personal_info.assert_called_once()
            self.mock_mysql.add_general_info.assert_called_once()

            mock_info.assert_called_once_with(
                self.add_page.add_page, "Success", "Employee added successfully!"
            )

    def test_clear_fields(self):
        self.add_page.ui.login_lineEdit.setText("test_login")
        self.add_page.ui.password_lineEdit.setText("test_password")
        self.add_page.ui.full_name_lineEdit.setText("Test Name")
        self.add_page.ui.sex_comboBox.addItem("Male")
        self.add_page.ui.sex_comboBox.setCurrentIndex(0)
        self.add_page.ui.department_comboBox.addItem("Finance", 1)
        self.add_page.ui.department_comboBox.setCurrentIndex(0)
        self.add_page.ui.position_comboBox.addItem("Manager", 2)
        self.add_page.ui.position_comboBox.setCurrentIndex(0)
        self.add_page.ui.hire_date_dateEdit.setDate(QtCore.QDate(2024, 4, 27))
        self.add_page.ui.experience_lineEdit.setText("5")
        self.add_page.ui.birth_date_dateEdit.setDate(QtCore.QDate(1990, 1, 1))

        self.add_page.clear_fields()

        self.assertEqual(self.add_page.ui.login_lineEdit.text(), "")
        self.assertEqual(self.add_page.ui.password_lineEdit.text(), "")
        self.assertEqual(self.add_page.ui.full_name_lineEdit.text(), "")
        self.assertEqual(self.add_page.ui.sex_comboBox.currentIndex(), 0)
        self.assertEqual(self.add_page.ui.department_comboBox.currentIndex(), 0)
        self.assertEqual(self.add_page.ui.position_comboBox.count(), 0)
        self.assertEqual(self.add_page.ui.hire_date_dateEdit.date(), QtCore.QDate.currentDate())
        self.assertEqual(self.add_page.ui.experience_lineEdit.text(), "")
        self.assertEqual(self.add_page.ui.birth_date_dateEdit.date(), QtCore.QDate.currentDate())

    def test_load_departments(self):
        self.mock_mysql.get_departments.return_value = [(1, "Finance"), (2, "HR")]

        self.add_page.load_departments()

        self.assertEqual(self.add_page.ui.department_comboBox.count(), 2)
        self.assertEqual(self.add_page.ui.department_comboBox.itemText(0), "Finance")
        self.assertEqual(self.add_page.ui.department_comboBox.itemText(1), "HR")

    def test_load_positions(self):
        self.mock_mysql.get_positions.return_value = [(1, "Manager"), (2, "Assistant")]

        self.add_page.load_positions(1)

        self.assertEqual(self.add_page.ui.position_comboBox.count(), 2)
        self.assertEqual(self.add_page.ui.position_comboBox.itemText(0), "Manager")
        self.assertEqual(self.add_page.ui.position_comboBox.itemText(1), "Assistant")

    def test_on_department_change(self):
        self.mock_mysql.get_positions.return_value = [(1, "Manager")]

        self.add_page.ui.department_comboBox.addItem("Finance", 1)
        self.add_page.ui.department_comboBox.setCurrentIndex(0)

        self.add_page.on_department_change()

        self.assertEqual(self.add_page.ui.position_comboBox.count(), 1)
        self.assertEqual(self.add_page.ui.position_comboBox.itemText(0), "Manager")

if __name__ == '__main__':
    unittest.main()