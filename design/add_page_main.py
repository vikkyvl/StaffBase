import re

from design.add_page import *
from imports import *

class AddPage(Connection):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.add_page = QtWidgets.QDialog(self.parent)
        self.add_page.setWindowFlags(self.add_page.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self.add_page)
        self.load_departments()

        self.ui.department_comboBox.currentIndexChanged.connect(self.on_department_change)
        self.ui.save_pushButton.clicked.connect(self.add_date)

        self.add_page.exec_()

    def validate_input(self, login, password, full_name, experience):
        login_pattern = re.compile(r"^[a-zA-Z]+\_[a-zA-Z]+$")
        if not login_pattern.match(login):
            QtWidgets.QMessageBox.critical(self.add_page, "Error", "Login must be in the format 'name_username'.")
            return False

        password_pattern = re.compile(r"^(?=.*[a-zA-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?\":{}|<>]).+$")
        if not password_pattern.match(password):
            QtWidgets.QMessageBox.critical(self.add_page, "Error",
                                           "Password must contain letters, digits, and symbols.")
            return False

        full_name_pattern = re.compile(r"^[A-Z][a-z]+\s[A-Z][a-z]+$")
        if not full_name_pattern.match(full_name):
            QtWidgets.QMessageBox.critical(self.add_page, "Error",
                                           "Full Name must consist of two words starting with uppercase letters.")
            return False

        if not experience.isdigit() or not (0 <= int(experience) <= 70):
            QtWidgets.QMessageBox.critical(self.add_page, "Error", "Experience must be a number between 0 and 70.")
            return False

        return True

    def add_date(self):
        employee_login = self.ui.login_lineEdit.text()
        employee_password = self.ui.password_lineEdit.text()
        employee_full_name = self.ui.full_name_lineEdit.text()
        employee_sex = self.ui.sex_comboBox.currentText()
        department_id = self.ui.department_comboBox.currentData()
        position_id = self.ui.position_comboBox.currentData()
        employee_hire_day = self.ui.hire_date_dateEdit.date().toString("yyyy-MM-dd")
        employee_experience = self.ui.experience_lineEdit.text()
        employee_birth_date = self.ui.birth_date_dateEdit.date().toString("yyyy-MM-dd")

        if not self.validate_input(employee_login, employee_password, employee_full_name, employee_experience):
            return

        new_user = User(employee_login, employee_password)
        new_user_id = new_user.get_ID()
        employee = Employee(new_user_id, employee_full_name)
        employee_personal_info = PersonalInfo(new_user_id, employee_birth_date, employee_sex)
        employee_general_info = GeneralInfo(new_user_id, department_id, position_id, employee_hire_day,
                                            employee_experience)

        try:
            self.redis_connection.add_employee(new_user)
            self.mysql_connection.add_employee(employee)
            self.mysql_connection.add_personal_info(employee_personal_info)
            self.mysql_connection.add_general_info(employee_general_info)

            QtWidgets.QMessageBox.information(self.add_page, "Success", "Employee added successfully!")

            self.clear_fields()
            self.add_page.accept()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.add_page, "Error", f"Failed to save employee data: {e}")

    def clear_fields(self):
        self.ui.login_lineEdit.clear()
        self.ui.password_lineEdit.clear()
        self.ui.full_name_lineEdit.clear()
        self.ui.sex_comboBox.setCurrentIndex(0)
        self.ui.department_comboBox.setCurrentIndex(0)
        self.ui.position_comboBox.clear()
        self.ui.hire_date_dateEdit.setDate(QtCore.QDate.currentDate())
        self.ui.experience_lineEdit.clear()
        self.ui.birth_date_dateEdit.setDate(QtCore.QDate.currentDate())

    def load_departments(self):
        departments = self.mysql_connection.get_departments()
        self.ui.department_comboBox.clear()
        for department_id, department_name in departments:
            self.ui.department_comboBox.addItem(department_name, department_id)

    def on_department_change(self):
        self.ui.position_comboBox.clear()
        selected_department_id = self.ui.department_comboBox.currentData()

        if selected_department_id:
            self.load_positions(selected_department_id)

    def load_positions(self, department_id):
        positions = self.mysql_connection.get_positions(department_id)
        for position_id, position_name in positions:
            self.ui.position_comboBox.addItem(position_name, position_id)

