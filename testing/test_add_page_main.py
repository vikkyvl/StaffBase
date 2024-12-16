import unittest
from unittest.mock import MagicMock, patch
from PyQt5 import QtWidgets, QtCore
from design.add_page_main import AddPage


class TestAddPage(unittest.TestCase):

    @patch('design.add_page_main.Redis')
    @patch('design.add_page_main.MySQL')
    @patch('design.add_page_main.QtWidgets.QMessageBox')
    @patch('design.add_page_main.QtWidgets.QDialog.exec_', return_value=None)  # Мокаємо виклик exec_
    def setUp(self, mock_exec, mock_messagebox, mock_mysql, mock_redis):
        # Ініціалізація QApplication для тестів
        self.app = QtWidgets.QApplication([])

        # Створення моків для Redis та MySQL
        self.mock_redis = mock_redis.return_value
        self.mock_mysql = mock_mysql.return_value
        self.mock_messagebox = mock_messagebox

        # Налаштування моків для методів бази даних
        self.mock_mysql.get_departments.return_value = [(1, "Finance"), (2, "HR")]
        self.mock_mysql.get_positions.return_value = [(1, "Manager"), (2, "Assistant")]

        # Створення інстансу AddPage без виклику exec_
        self.add_page = AddPage()

    def tearDown(self):
        self.app.quit()

    def test_validate_input_success(self):
        valid_login = "john_doe"
        valid_password = "Password123!"
        valid_full_name = "John Doe"
        valid_experience = "5"

        result = self.add_page.validate_input(valid_login, valid_password, valid_full_name, valid_experience)
        self.assertTrue(result)

    def test_validate_input_invalid_login(self):
        invalid_login = "johndoe"
        valid_password = "Password123!"
        valid_full_name = "John Doe"
        valid_experience = "5"

        result = self.add_page.validate_input(invalid_login, valid_password, valid_full_name, valid_experience)
        self.assertFalse(result)
        self.mock_messagebox.critical.assert_called_once_with(self.add_page.add_page, "Error",
                                                              "Login must be in the format 'name_username'.")

    def test_add_date_success(self):
        # Заповнення полів форми
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

        # Налаштування моків для додавання
        self.mock_redis.add_employee = MagicMock()
        self.mock_mysql.add_employee = MagicMock()
        self.mock_mysql.add_personal_info = MagicMock()
        self.mock_mysql.add_general_info = MagicMock()

        self.add_page.add_date()

        self.mock_redis.add_employee.assert_called_once()
        self.mock_mysql.add_employee.assert_called_once()
        self.mock_mysql.add_personal_info.assert_called_once()
        self.mock_mysql.add_general_info.assert_called_once()
        self.mock_messagebox.information.assert_called_once_with(
            self.add_page.add_page, "Success", "Employee added successfully!"
        )

    def test_add_date_invalid_input(self):
        # Заповнення невалідних даних
        self.add_page.ui.login_lineEdit.setText("john_doe")
        self.add_page.ui.password_lineEdit.setText("Password123!")
        self.add_page.ui.full_name_lineEdit.setText("John Doe")
        self.add_page.ui.experience_lineEdit.setText("5")

        # Виклик методу для додавання
        self.add_page.add_date()

        # Перевірка, що методи не викликались
        self.mock_redis.add_employee.assert_not_called()
        self.mock_mysql.add_employee.assert_not_called()
        self.mock_mysql.add_personal_info.assert_not_called()
        self.mock_mysql.add_general_info.assert_not_called()
        self.mock_messagebox.critical.assert_called()


if __name__ == '__main__':
    unittest.main()
