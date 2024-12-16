import re
from design.edit_page import *
from imports import *

class EditPage:
    def __init__(self, redis_connection, mysql_connection, parent=None, worker_table=None):
        self.parent = parent
        self.worker_table = worker_table
        self.redis_connection = redis_connection
        self.mysql_connection = mysql_connection

        selected_row = self.worker_table.currentIndex().row()
        if selected_row == -1:
            QtWidgets.QMessageBox.warning(None, "Warning", "No employee selected!")
            return

        self.edit_page = QtWidgets.QDialog(self.parent)
        self.edit_page.setWindowFlags(self.edit_page.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self.edit_page)
        self.load_departments()

        self.ui.update_pushButton.clicked.connect(self.update_employee_data)

        self.ui.department_comboBox.currentIndexChanged.connect(self.on_department_change)

        self.fill_fields_from_table()

        self.edit_page.exec_()

    def validate_input(self, login, password, full_name, experience):
        login_pattern = re.compile(r"^[a-zA-Z]+\_[a-zA-Z]+$")
        if not login_pattern.match(login):
            QtWidgets.QMessageBox.critical(self.edit_page, "Error", "Login must be in the format 'name_username'.")
            return False

        password_pattern = re.compile(r"^(?=.*[a-zA-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]).+$")
        if not password_pattern.match(password):
            QtWidgets.QMessageBox.critical(self.edit_page, "Error",
                                           "Password must contain letters, digits, and symbols.")
            return False

        full_name_pattern = re.compile(r"^[A-Z][a-z]+\s[A-Z][a-z]+$")
        if not full_name_pattern.match(full_name):
            QtWidgets.QMessageBox.critical(self.edit_page, "Error",
                                           "Full Name must consist of two words starting with uppercase letters.")
            return False

        if not experience.isdigit() or not (0 <= int(experience) <= 70):
            QtWidgets.QMessageBox.critical(self.edit_page, "Error", "Experience must be a number between 0 and 70.")
            return False

        return True

    def fill_fields_from_table(self):
        model = self.worker_table.model()
        selected_row = self.worker_table.currentIndex().row()

        self.ui.login_lineEdit.setText(model.index(selected_row, 1).data())
        self.ui.password_lineEdit.setText(model.index(selected_row, 2).data())
        self.ui.full_name_lineEdit.setText(model.index(selected_row, 3).data())
        self.ui.sex_comboBox.setCurrentText(model.index(selected_row, 4).data())
        self.ui.department_comboBox.setCurrentText(model.index(selected_row, 5).data())
        self.ui.position_comboBox.setCurrentText(model.index(selected_row, 6).data())
        self.ui.hire_date_dateEdit.setDate(QtCore.QDate.fromString(model.index(selected_row, 7).data(), "yyyy-MM-dd"))
        self.ui.experience_lineEdit.setText(model.index(selected_row, 8).data())
        self.ui.birth_date_dateEdit.setDate(QtCore.QDate.fromString(model.index(selected_row, 10).data(), "yyyy-MM-dd"))
        self.ui.phone_number_lineEdit.setText(model.index(selected_row, 11).data())
        self.ui.maritual_status_comboBox.setCurrentText(model.index(selected_row, 12).data())
        self.ui.email_lineEdit.setText(model.index(selected_row, 13).data())

    def load_departments(self):
        departments = self.mysql_connection.get_departments()
        self.ui.department_comboBox.clear()
        for department_id, department_name in departments:
            self.ui.department_comboBox.addItem(department_name, department_id)

    def load_positions(self, department_id):
        positions = self.mysql_connection.get_positions(department_id)
        self.ui.position_comboBox.clear()
        for position_id, position_name in positions:
            self.ui.position_comboBox.addItem(position_name, position_id)

    def on_department_change(self):
        selected_department_id = self.ui.department_comboBox.currentData()
        if selected_department_id:
            self.load_positions(selected_department_id)

    def update_employee_data(self):
        model = self.worker_table.model()
        selected_row = self.worker_table.currentIndex().row()

        old_login = model.index(selected_row, 1).data()
        old_password = model.index(selected_row, 2).data()

        new_login = self.ui.login_lineEdit.text()
        new_password = self.ui.password_lineEdit.text()
        new_full_name = self.ui.full_name_lineEdit.text()
        new_experience = self.ui.experience_lineEdit.text()

        if not self.validate_input(new_login, new_password, new_full_name, new_experience):
            return

        if new_login != old_login:
            login_updated = self.redis_connection.update_employee_login(old_login, new_login)
            if not login_updated:
                QtWidgets.QMessageBox.critical(self.edit_page, "Error",
                                               "Failed to update login. The new login may already exist.")
                return

        if new_password != old_password:
            password_updated = self.redis_connection.update_employee_password(new_login, new_password)
            if not password_updated:
                QtWidgets.QMessageBox.critical(self.edit_page, "Error", "Failed to update password.")
                return

        employee_id = model.index(selected_row, 0).data()

        data = {
            "employee_id": employee_id,
            "login": new_login,
            "password": new_password,
            "full_name": self.ui.full_name_lineEdit.text(),
            "sex": self.ui.sex_comboBox.currentText(),
            "department_id": self.ui.department_comboBox.currentData(),
            "position_id": self.ui.position_comboBox.currentData(),
            "hire_date": self.ui.hire_date_dateEdit.date().toString("yyyy-MM-dd"),
            "experience": self.ui.experience_lineEdit.text(),
            "birth_date": self.ui.birth_date_dateEdit.date().toString("yyyy-MM-dd"),
            "phone_number": self.ui.phone_number_lineEdit.text(),
            "marital_status": self.ui.maritual_status_comboBox.currentText(),
            "email": self.ui.email_lineEdit.text(),
        }

        success = self.mysql_connection.update_employee(data)

        if success:
            QtWidgets.QMessageBox.information(self.edit_page, "Success", "Employee data updated successfully!")
            self.edit_page.accept()
        else:
            QtWidgets.QMessageBox.critical(self.edit_page, "Error", "Failed to update employee data.")
