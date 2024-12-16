import re
from design.edit_page import *
from imports import *


class EditPage():
    def __init__(self, parent=None, employee_data=None):
        self.parent = parent
        self.employee_data = employee_data
        self.edit_page = QtWidgets.QDialog(self.parent)
        self.edit_page.setWindowFlags(self.edit_page.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self.edit_page)

        self.redis_connection = Redis()
        self.mysql_connection = MySQL()

        self.load_departments()
        self.populate_fields()

        self.ui.update_pushButton.clicked.connect(self.update_employee_data)

        self.edit_page.exec_()

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

    def populate_fields(self):
        if not self.employee_data:
            QtWidgets.QMessageBox.critical(self.edit_page, "Error", "No employee selected for editing!")
            self.edit_page.reject()
            return

        self.ui.login_lineEdit.setText(self.employee_data.get("login", ""))
        self.ui.password_lineEdit.setText(self.employee_data.get("password", ""))
        self.ui.full_name_lineEdit.setText(self.employee_data.get("full_name", ""))
        self.ui.sex_comboBox.setCurrentText(self.employee_data.get("sex", "Male"))
        self.ui.hire_date_dateEdit.setDate(QtCore.QDate.fromString(self.employee_data.get("hire_date", "2000-01-01"), "yyyy-MM-dd"))
        self.ui.experience_lineEdit.setText(str(self.employee_data.get("previous_experience", 0)))
        self.ui.birth_date_dateEdit.setDate(QtCore.QDate.fromString(self.employee_data.get("birth_date", "2000-01-01"), "yyyy-MM-dd"))

        department_id = self.employee_data.get("department_id")
        self.load_departments()
        department_index = self.ui.department_comboBox.findData(department_id)
        if department_index != -1:
            self.ui.department_comboBox.setCurrentIndex(department_index)
            self.load_positions(department_id)

        position_id = self.employee_data.get("position_id")
        position_index = self.ui.position_comboBox.findData(position_id)
        if position_index != -1:
            self.ui.position_comboBox.setCurrentIndex(position_index)

    def update_employee_data(self):
        login = self.ui.login_lineEdit.text()
        password = self.ui.password_lineEdit.text()
        full_name = self.ui.full_name_lineEdit.text()
        sex = self.ui.sex_comboBox.currentText()
        department_id = self.ui.department_comboBox.currentData()
        position_id = self.ui.position_comboBox.currentData()
        hire_date = self.ui.hire_date_dateEdit.date().toString("yyyy-MM-dd")
        experience = self.ui.experience_lineEdit.text()
        birth_date = self.ui.birth_date_dateEdit.date().toString("yyyy-MM-dd")

        try:
            self.mysql_connection.cursor.execute("""
                UPDATE GeneralInfo
                SET department_id = %s, position_id = %s, hire_date = %s, previous_experience = %s
                WHERE employee_id = %s
            """, (department_id, position_id, hire_date, experience, self.employee_data["employee_id"]))

            self.mysql_connection.cursor.execute("""
                UPDATE PersonalInfo
                SET birth_date = %s, sex = %s
                WHERE employee_id = %s
            """, (birth_date, sex, self.employee_data["employee_id"]))

            self.mysql_connection.cursor.execute("""
                UPDATE Employee
                SET login = %s, password = %s, full_name = %s
                WHERE employee_id = %s
            """, (login, password, full_name, self.employee_data["employee_id"]))

            self.mysql_connection.mydb.commit()
            QtWidgets.QMessageBox.information(self.edit_page, "Success", "Employee data updated successfully!")
            self.edit_page.accept()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.edit_page, "Error", f"Failed to update employee data: {e}")

