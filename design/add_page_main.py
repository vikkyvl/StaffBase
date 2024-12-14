from design.add_page import *
from imports import *

class AddPage:
    def __init__(self, parent=None):
        self.parent = parent
        self.add_page = QtWidgets.QDialog(self.parent)
        self.add_page.setWindowFlags(self.add_page.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self.add_page)

        self.redis_connection = Redis()
        self.mysql_connection = MySQL()
        self.load_departments()

        # Прив'язка сигналів
        self.ui.department_comboBox.currentIndexChanged.connect(self.on_department_change)
        self.ui.save_pushButton.clicked.connect(self.add_date)

        self.add_page.exec_()

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



        new_user = User(employee_login, employee_password)
        new_user_id = new_user.get_ID()
        employee = Employee(new_user_id, employee_full_name)
        employee_personal_info = PersonalInfo(new_user_id, employee_birth_date, employee_sex)
        employee_general_info = GeneralInfo(new_user_id, department_id, position_id, employee_hire_day, employee_experience)

        try:
            self.redis_connection.add_employee(new_user)
            self.mysql_connection.add_employee(employee)
            self.mysql_connection.add_personal_info(employee_personal_info)
            self.mysql_connection.add_general_info(employee_general_info)
            QtWidgets.QMessageBox.information(self.add_page, "Success", "Employee added successfully!")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.add_page, "Error", f"Failed to save employee data: {e}")

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

