from PyQt5 import QtWidgets
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QApplication
from design.admin_page import Ui_Form
from design.add_page_main import *
from design.edit_page_main import *


class AdminPage(QtWidgets.QWidget):
    def __init__(self, redis_connection, mysql_connection):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.page_buttons = {
            self.ui.manage_employees_pushButton: 1,
            self.ui.calculate_salary_pushButton: 2,
            self.ui.generate_report_pushButton: 3,
            self.ui.add_pushButton: 4,
            self.ui.exit_pushButton: 5,
            self.ui.view_pushButton: 6,
            self.ui.delete_pushButton: 7,
            self.ui.edit_pushButton: 8,
            self.ui.add_leave_pushButton: 9,
            self.ui.view_leave_pushButton: 10,
            self.ui.edit_leave_pushButton: 11,
        }

        self.redis_connection = redis_connection
        self.mysql_connection = mysql_connection

        for button, page in self.page_buttons.items():
            button.clicked.connect(self.create_switch_page_handler(page))

        self.setup_worker_table()
        self.load_workers_into_combobox()
        self.ui.worker_leaves_tableView.doubleClicked.connect(self.save_leave_request_changes)

    def create_switch_page_handler(self, page):
        def handler():
            self.switch_page(page)

        return handler


    def switch_page(self, index):
        self.ui.stackedWidget.setCurrentIndex(index)

        match index:
            case 4:
                self.add_info_worker()
            case 5:
                self.confirm_exit()
            case 6:
                self.load_workers_data()
            case 7:
                self.delete_workers_data()
            case 8:
                self.edit_info_worker()
            case 9:
                self.add_leave_request()
            case 10:
                self.view_leave_requests()
            case 11:
                self.edit_leave_request()

    def add_info_worker(self):
        add_new_worker = AddPage(redis_connection=self.redis_connection, mysql_connection=self.mysql_connection)

    def edit_info_worker(self):
        edit_worker = EditPage(redis_connection=self.redis_connection, mysql_connection=self.mysql_connection, worker_table=self.ui.worker_tableView)

    def confirm_exit(self):
        reply = QMessageBox.question(
            self,
            "Exit Confirmation",
            "Are you sure you want to exit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            QApplication.instance().quit()
        else:
            pass

    def setup_worker_table(self):
        model = QStandardItemModel()

        model.setHorizontalHeaderLabels([
            "ID", "Login", "Password", "Full Name", "Sex",
            "Department", "Position", "Hire Date", "Previous Experience",
            "Total Experience", "Birth Date", "Phone Number",
            "Marital Status", "Email"
        ])

        self.ui.worker_tableView.setModel(model)
        self.ui.worker_tableView.horizontalHeader().setStretchLastSection(True)
        self.ui.worker_tableView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.ui.worker_tableView.resizeColumnsToContents()
        self.ui.worker_tableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Interactive)

    def load_workers_data(self):
        model = self.ui.worker_tableView.model()
        model.removeRows(0, model.rowCount())

        redis_users = self.redis_connection.get_all_users()

        for user in redis_users:
            user_id = user["id"]
            login = user["login"]
            password = user["password"]

            result = self.mysql_connection.get_worker_details(user_id)

            if result:
                (full_name, sex, department, position, hire_date,
                 previous_experience, total_experience, birth_date,
                 phone_number, marital_status, email) = result

                row = [
                    user_id, login, password, full_name, sex, department,
                    position, str(hire_date), str(previous_experience), str(total_experience),
                    str(birth_date), phone_number if phone_number else "",
                    marital_status if marital_status else "",
                    email if email else ""
                ]

                model.insertRow(model.rowCount())
                for col, value in enumerate(row):
                    model.setData(model.index(model.rowCount() - 1, col), value)

        self.ui.worker_tableView.resizeColumnsToContents()

    def delete_workers_data(self):
        selected_indexes = self.ui.worker_tableView.selectionModel().selectedRows()
        if not selected_indexes:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select a worker to delete.")
            return

        selected_row = selected_indexes[0]
        user_id = self.ui.worker_tableView.model().index(selected_row.row(), 0).data()
        login = self.ui.worker_tableView.model().index(selected_row.row(), 1).data()

        confirmation = QtWidgets.QMessageBox.question(
            self, "Delete Confirmation",
            f"Are you sure you want to delete the worker with ID '{user_id}' and login '{login}'?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )

        if confirmation == QtWidgets.QMessageBox.Yes:
            try:
                self.mysql_connection.delete_worker_by_id(user_id)
                self.redis_connection.delete_employee(login)

                QtWidgets.QMessageBox.information(self, "Success", f"Worker '{login}' has been successfully deleted.")
                self.load_workers_data()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to delete worker: {e}")

    def load_workers_into_combobox(self):
        try:
            query = "SELECT employee_id, full_name FROM Employee"
            self.mysql_connection.cursor.execute(query)
            workers = self.mysql_connection.cursor.fetchall()

            self.ui.worker_leave_comboBox.clear()

            for worker_id, full_name in workers:
                self.ui.worker_leave_comboBox.addItem(full_name, worker_id)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load workers: {e}")

    def add_leave_request(self):
        worker_name = self.ui.worker_leave_comboBox.currentText()
        leave_type = self.ui.type_leave_comboBox.currentText()
        start_date = self.ui.start_date_dateEdit.date().toString("yyyy-MM-dd")
        end_date = self.ui.end_date_dateEdit.date().toString("yyyy-MM-dd")

        if not worker_name or not leave_type:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select a worker and leave type.")
            return

        employee_id = self.mysql_connection.get_employee_id_by_name(worker_name)
        if not employee_id:
            QtWidgets.QMessageBox.critical(self, "Error", "Failed to find employee ID.")
            return

        try:
            self.mysql_connection.add_leave_request(employee_id, leave_type, start_date, end_date)

            model = self.ui.worker_leaves_tableView.model()
            if not model:
                model = QStandardItemModel()
                model.setHorizontalHeaderLabels(["Worker", "Leave Type", "Start Date", "End Date", "Duration"])
                self.ui.worker_leaves_tableView.setModel(model)

            start_date_qt = self.ui.start_date_dateEdit.date()
            end_date_qt = self.ui.end_date_dateEdit.date()
            duration = start_date_qt.daysTo(end_date_qt) + 1

            row = [worker_name, leave_type, start_date, end_date, str(duration)]
            model.insertRow(model.rowCount())
            for col, value in enumerate(row):
                model.setData(model.index(model.rowCount() - 1, col), value)

            self.ui.worker_leaves_tableView.resizeColumnsToContents()
            QtWidgets.QMessageBox.information(self, "Success", "Leave request added successfully!")

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to add leave request: {e}")

    def view_leave_requests(self):
        try:
            leave_requests = self.mysql_connection.get_all_leave_requests()

            model = self.ui.worker_leaves_tableView.model()
            if not model:
                model = QStandardItemModel()
                model.setHorizontalHeaderLabels(["Worker", "Leave Type", "Start Date", "End Date", "Duration"])
                self.ui.worker_leaves_tableView.setModel(model)

            model.removeRows(0, model.rowCount())

            for leave in leave_requests:
                model.insertRow(model.rowCount())
                for col, value in enumerate(leave):
                    model.setData(model.index(model.rowCount() - 1, col), str(value))

            self.ui.worker_leaves_tableView.resizeColumnsToContents()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load leave requests: {e}")

    def edit_leave_request(self):
        selected_indexes = self.ui.worker_leaves_tableView.selectionModel().selectedRows()
        if not selected_indexes:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select a leave request to edit.")
            return

        # Дозволити редагування вибраного рядка
        self.ui.worker_leaves_tableView.setEditTriggers(
            QtWidgets.QAbstractItemView.DoubleClicked | QtWidgets.QAbstractItemView.EditKeyPressed
        )
        QtWidgets.QMessageBox.information(
            self, "Info", "You can now edit the selected leave request. Press Enter to save changes."
        )

    def save_leave_request_changes(self):
        selected_indexes = self.ui.worker_leaves_tableView.selectionModel().selectedRows()
        if not selected_indexes:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select a leave request to save changes.")
            return

        selected_row = selected_indexes[0].row()

        # Зчитування даних із вибраного рядка
        worker_name = self.ui.worker_leaves_tableView.model().index(selected_row, 0).data()
        leave_type = self.ui.worker_leaves_tableView.model().index(selected_row, 1).data()
        start_date = self.ui.worker_leaves_tableView.model().index(selected_row, 2).data()
        end_date = self.ui.worker_leaves_tableView.model().index(selected_row, 3).data()

        # Отримання employee_id за ім'ям працівника
        employee_id = self.mysql_connection.get_employee_id_by_name(worker_name)
        if not employee_id:
            QtWidgets.QMessageBox.critical(self, "Error", "Failed to find employee ID.")
            return

        try:
            # Оновлення запису у базі даних
            self.mysql_connection.update_leave_request(employee_id, leave_type, start_date, end_date)
            QtWidgets.QMessageBox.information(self, "Success", "Leave request updated successfully!")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to update leave request: {e}")

