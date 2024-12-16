import re
from design.edit_page import *
from imports import *


class EditPage:
    def __init__(self, redis_connection, mysql_connection, parent=None, worker_table=None):
        self.parent = parent
        self.worker_table = worker_table
        self.redis_connection = redis_connection
        self.mysql_connection = mysql_connection
        self.edit_page = QtWidgets.QDialog(self.parent)
        self.edit_page.setWindowFlags(self.edit_page.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self.edit_page)
        self.load_departments()

        # Підключення зміни відділу до оновлення посад
        self.ui.department_comboBox.currentIndexChanged.connect(self.on_department_change)

        # Обробник кнопки оновлення
        # self.ui.update_pushButton.clicked.connect(self.update_employee_data)

        # Заповнення полів з виділеного рядка
        self.fill_fields_from_table()

        self.edit_page.exec_()

    def fill_fields_from_table(self):
        """
        Заповнює поля редагування даними з виділеного рядка таблиці.
        """
        selected_row = self.worker_table.currentIndex().row()
        if selected_row == -1:
            QtWidgets.QMessageBox.warning(self.edit_page, "Увага", "Не вибрано жодного працівника!")
            return

        model = self.worker_table.model()

        self.ui.login_lineEdit.setText(model.index(selected_row, 1).data())  # Login
        self.ui.password_lineEdit.setText(model.index(selected_row, 2).data())  # Password
        self.ui.full_name_lineEdit.setText(model.index(selected_row, 3).data())  # Full Name
        self.ui.sex_comboBox.setCurrentText(model.index(selected_row, 4).data())  # Sex
        self.ui.department_comboBox.setCurrentText(model.index(selected_row, 5).data())  # Department
        self.ui.position_comboBox.setCurrentText(model.index(selected_row, 6).data())  # Position
        self.ui.hire_date_dateEdit.setDate(
            QtCore.QDate.fromString(model.index(selected_row, 7).data(), "yyyy-MM-dd"))  # Hire Date
        self.ui.experience_lineEdit.setText(model.index(selected_row, 8).data())  # Previous Experience
        self.ui.birth_date_dateEdit.setDate(
            QtCore.QDate.fromString(model.index(selected_row, 10).data(), "yyyy-MM-dd"))  # Birth Date
        self.ui.phone_number_lineEdit.setText(model.index(selected_row, 11).data())  # Phone Number
        self.ui.maritual_status_comboBox.setCurrentText(model.index(selected_row, 12).data())  # Marital Status
        self.ui.email_lineEdit.setText(model.index(selected_row, 13).data())  # Email

    def load_departments(self):
        """
        Завантажує список відділів у ComboBox.
        """
        departments = self.mysql_connection.get_departments()
        self.ui.department_comboBox.clear()
        for department_id, department_name in departments:
            self.ui.department_comboBox.addItem(department_name, department_id)

    def load_positions(self, department_id):
        """
        Завантажує список посад у ComboBox залежно від вибраного відділу.
        """
        positions = self.mysql_connection.get_positions(department_id)
        self.ui.position_comboBox.clear()
        for position_id, position_name in positions:
            self.ui.position_comboBox.addItem(position_name, position_id)

    def on_department_change(self):
        """
        Оновлює список посад при зміні вибраного відділу.
        """
        selected_department_id = self.ui.department_comboBox.currentData()
        if selected_department_id:
            self.load_positions(selected_department_id)

    def update_employee_data(self):
        """
        Оновлює дані працівника в базі даних.
        """
        # Отримання даних з полів
        data = {
            "login": self.ui.login_lineEdit.text(),
            "password": self.ui.password_lineEdit.text(),
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

        # Оновлення даних у MySQL
        success = self.mysql_connection.update_employee(data)
        if success:
            QtWidgets.QMessageBox.information(self.edit_page, "Успіх", "Дані успішно оновлено!")
            self.edit_page.accept()
        else:
            QtWidgets.QMessageBox.critical(self.edit_page, "Помилка", "Не вдалося оновити дані.")
    #     self.load_departments()
    #     self.populate_fields()
    #
    #     self.ui.update_pushButton.clicked.connect(self.update_employee_data)
    #
    #     self.edit_page.exec_()
    #
    # def load_departments(self):
    #     departments = self.mysql_connection.get_departments()
    #     self.ui.department_comboBox.clear()
    #     for department_id, department_name in departments:
    #         self.ui.department_comboBox.addItem(department_name, department_id)
    #
    # def load_positions(self, department_id):
    #     positions = self.mysql_connection.get_positions(department_id)
    #     self.ui.position_comboBox.clear()
    #     for position_id, position_name in positions:
    #         self.ui.position_comboBox.addItem(position_name, position_id)
    #
    # def populate_fields(self):
    #     if not self.worker_table:
    #         QtWidgets.QMessageBox.critical(self.edit_page, "Error", "No worker table provided!")
    #         self.edit_page.reject()
    #         return
    #
    #     selected_row = self.worker_table.selectionModel().currentIndex().row()
    #     if selected_row == -1:
    #         QtWidgets.QMessageBox.critical(self.edit_page, "Error", "No employee selected for editing!")
    #         self.edit_page.reject()
    #         return
    #
    #     model = self.worker_table.model()
    #
    #     login = model.data(model.index(selected_row, 1)) or ""
    #     password = model.data(model.index(selected_row, 2)) or ""
    #     full_name = model.data(model.index(selected_row, 3)) or ""
    #     sex = model.data(model.index(selected_row, 4)) or "Male"
    #     department_name = model.data(model.index(selected_row, 5)) or ""
    #     position_name = model.data(model.index(selected_row, 6)) or ""
    #     hire_date = model.data(model.index(selected_row, 7)) or "2000-01-01"
    #     experience = model.data(model.index(selected_row, 8)) or "0"
    #     birth_date = model.data(model.index(selected_row, 10)) or "2000-01-01"
    #     phone_number = model.data(model.index(selected_row, 11)) or ""
    #     marital_status = model.data(model.index(selected_row, 12)) or ""
    #     email = model.data(model.index(selected_row, 13)) or ""
    #
    #     self.ui.login_lineEdit.setText(login)
    #     self.ui.password_lineEdit.setText(password)
    #     self.ui.full_name_lineEdit.setText(full_name)
    #     self.ui.sex_comboBox.setCurrentText(sex)
    #     self.ui.hire_date_dateEdit.setDate(QtCore.QDate.fromString(hire_date, "yyyy-MM-dd"))
    #     self.ui.experience_lineEdit.setText(experience)
    #     self.ui.birth_date_dateEdit.setDate(QtCore.QDate.fromString(birth_date, "yyyy-MM-dd"))
    #     self.ui.phone_number_lineEdit.setText(phone_number)
    #     self.ui.maritual_status_comboBox.setCurrentText(marital_status)
    #     self.ui.email_lineEdit.setText(email)
    #
    #     self.load_departments()
    #     department_index = self.ui.department_comboBox.findText(department_name)
    #     if department_index != -1:
    #         self.ui.department_comboBox.setCurrentIndex(department_index)
    #         department_id = self.ui.department_comboBox.currentData()
    #         self.load_positions(department_id)
    #
    #     position_index = self.ui.position_comboBox.findText(position_name)
    #     if position_index != -1:
    #         self.ui.position_comboBox.setCurrentIndex(position_index)
    #
    # def update_employee_data(self):
    #     login = self.ui.login_lineEdit.text()
    #     password = self.ui.password_lineEdit.text()
    #     full_name = self.ui.full_name_lineEdit.text()
    #     sex = self.ui.sex_comboBox.currentText()
    #     department_id = self.ui.department_comboBox.currentData()
    #     position_id = self.ui.position_comboBox.currentData()
    #     hire_date = self.ui.hire_date_dateEdit.date().toString("yyyy-MM-dd")
    #     experience = self.ui.experience_lineEdit.text()
    #     birth_date = self.ui.birth_date_dateEdit.date().toString("yyyy-MM-dd")
    #
    #     try:
    #         self.mysql_connection.cursor.execute("""
    #                     UPDATE GeneralInfo
    #                     SET department_id = %s, position_id = %s, hire_date = %s, previous_experience = %s
    #                     WHERE employee_id = %s
    #                 """, (department_id, position_id, hire_date, experience, self.employee_data["employee_id"]))
    #
    #         self.mysql_connection.cursor.execute("""
    #                     UPDATE PersonalInfo
    #                     SET birth_date = %s, sex = %s
    #                     WHERE employee_id = %s
    #                 """, (birth_date, sex, self.employee_data["employee_id"]))
    #
    #         self.mysql_connection.cursor.execute("""
    #                     UPDATE Employee
    #                     SET login = %s, password = %s, full_name = %s
    #                     WHERE employee_id = %s
    #                 """, (login, password, full_name, self.employee_data["employee_id"]))
    #
    #         self.mysql_connection.mydb.commit()
    #         QtWidgets.QMessageBox.information(self.edit_page, "Success", "Employee data updated successfully!")
    #         self.edit_page.accept()
    #     except Exception as e:
    #         QtWidgets.QMessageBox.critical(self.edit_page, "Error", f"Failed to update employee data: {e}")

