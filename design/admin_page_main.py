from decimal import Decimal

from PyQt5 import QtWidgets
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QApplication
from design.admin_page import Ui_Form
from design.add_page_main import *
from design.edit_leave_page_main import *
from design.edit_page_main import *
from classes.calculation_salary import CalculationSalary
from classes.salary import Salary

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
            self.ui.delete_leave_pushButton: 12,
            self.ui.calculate_pushButton: 13,
            self.ui.view_salary_pushButton: 14,
            self.ui.generate_report_pushButton_2: 15,
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
            case 2:
                self.load_workers_into_combobox()
            case 12:
                self.delete_leave_request()
            case 13:
                self.calculate_salary()
            case 14:
                self.view_salaries()
            case 15:
                self.generate_report()

    def add_info_worker(self):
        add_new_worker = AddPage(redis_connection=self.redis_connection, mysql_connection=self.mysql_connection)

    def edit_info_worker(self):
        edit_worker = EditPage(redis_connection=self.redis_connection, mysql_connection=self.mysql_connection, worker_table=self.ui.worker_tableView)

    def edit_leave_request(self):
        edit_leave_page = EditLeavePage(redis_connection=self.redis_connection, mysql_connection=self.mysql_connection, worker_leaves_tableView=self.ui.worker_leaves_tableView)

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
            workers = self.mysql_connection.get_all_workers()
            self.ui.worker_salary_comboBox.clear()
            self.ui.worker_leave_comboBox.clear()

            for worker_id, full_name in workers:
                self.ui.worker_leave_comboBox.addItem(full_name, worker_id)
                self.ui.worker_salary_comboBox.addItem(full_name, worker_id)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load workers: {e}")

    def add_leave_request(self):
        worker_name = self.ui.worker_leave_comboBox.currentText()
        leave_type = self.ui.type_leave_comboBox.currentText()
        start_date_qt = self.ui.start_date_dateEdit.date()
        end_date_qt = self.ui.end_date_dateEdit.date()

        start_date = start_date_qt.toString("yyyy-MM-dd")
        end_date = end_date_qt.toString("yyyy-MM-dd")

        if not worker_name or not leave_type:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select a worker and leave type.")
            return

        if start_date_qt > end_date_qt:
            QtWidgets.QMessageBox.critical(self, "Error", "Start date cannot be later than end date.")
            return

        if start_date_qt.year() != end_date_qt.year() or start_date_qt.month() != end_date_qt.month():
            QtWidgets.QMessageBox.critical(self,"Error","Leave request dates must be within the same month and year.")
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

    def save_leave_request_changes(self):
        selected_indexes = self.ui.worker_leaves_tableView.selectionModel().selectedRows()
        if not selected_indexes:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select a leave request to save changes.")
            return

        selected_row = selected_indexes[0].row()

        worker_name = self.ui.worker_leaves_tableView.model().index(selected_row, 0).data()
        leave_type = self.ui.worker_leaves_tableView.model().index(selected_row, 1).data()
        start_date = self.ui.worker_leaves_tableView.model().index(selected_row, 2).data()
        end_date = self.ui.worker_leaves_tableView.model().index(selected_row, 3).data()

        employee_id = self.mysql_connection.get_employee_id_by_name(worker_name)
        if not employee_id:
            QtWidgets.QMessageBox.critical(self, "Error", "Failed to find employee ID.")
            return

        try:
            self.mysql_connection.update_leave_request(employee_id, leave_type, start_date, end_date)
            QtWidgets.QMessageBox.information(self, "Success", "Leave request updated successfully!")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to update leave request: {e}")

    def delete_leave_request(self):
        selected_indexes = self.ui.worker_leaves_tableView.selectionModel().selectedRows()
        if not selected_indexes:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select a leave request to delete.")
            return

        selected_row = selected_indexes[0].row()

        worker_name = self.ui.worker_leaves_tableView.model().index(selected_row, 0).data()
        leave_type = self.ui.worker_leaves_tableView.model().index(selected_row, 1).data()
        start_date = self.ui.worker_leaves_tableView.model().index(selected_row, 2).data()
        end_date = self.ui.worker_leaves_tableView.model().index(selected_row, 3).data()

        confirmation = QtWidgets.QMessageBox.question(
            self,
            "Delete Confirmation",
            f"Are you sure you want to delete the leave request for '{worker_name}' ({leave_type}) "
            f"from {start_date} to {end_date}?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )

        if confirmation == QtWidgets.QMessageBox.Yes:
            employee_id = self.mysql_connection.get_employee_id_by_name(worker_name)
            if not employee_id:
                QtWidgets.QMessageBox.critical(self, "Error", "Failed to find employee ID.")
                return

            try:
                self.mysql_connection.delete_leave_request(employee_id, leave_type, start_date, end_date)

                self.ui.worker_leaves_tableView.model().removeRow(selected_row)

                QtWidgets.QMessageBox.information(self, "Success", "Leave request deleted successfully!")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to delete leave request: {e}")

    def calculate_salary(self):
        worker_name = self.ui.worker_salary_comboBox.currentText()
        month = self.ui.month_comboBox.currentIndex()
        year = self.ui.year_dateEdit.date().year()
        salary_month = f"{year}-{month:02d}"

        try:
            premium = Decimal(self.ui.premium_lineEdit.text().strip() or "0")
        except Exception as e:
            raise ValueError("Invalid premium value") from e

        employee_id = self.mysql_connection.get_employee_id_by_name(worker_name)
        if not employee_id:
            raise ValueError(f"No employee found with name {worker_name}")

        employee_position_info = self.mysql_connection.get_employee_info_for_calculation_salary(employee_id)
        if not employee_position_info:
            raise ValueError(f"No employee position info found for employee_id {employee_id}")

        employee_leave_info = self.mysql_connection.get_employee_leaves(employee_id, salary_month)

        calculated_salary = CalculationSalary().calculation_salary(
            month, year, premium, employee_position_info, employee_leave_info
        )

        salary = Salary(employee_id, salary_month, calculated_salary)
        self.mysql_connection.add_employee_salary(salary)

    def view_salaries(self):
        try:
            salaries = self.mysql_connection.get_all_salaries_with_names()

            table = self.ui.worker_salary_tableWidget
            table.clear()
            table.setColumnCount(3)
            table.setHorizontalHeaderLabels(["Worker", "Date", "Salary"])

            table.setRowCount(len(salaries))
            for row_idx, (full_name, salary_month, salary_amount) in enumerate(salaries):
                table.setItem(row_idx, 0, QtWidgets.QTableWidgetItem(full_name))
                table.setItem(row_idx, 1, QtWidgets.QTableWidgetItem(salary_month))
                table.setItem(row_idx, 2, QtWidgets.QTableWidgetItem(str(salary_amount)))

            table.resizeColumnsToContents()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load salaries: {e}")

    def generate_report(self):
        selected_report = self.ui.number_report_comboBox.currentIndex()

        if selected_report == 1:
            results = self.mysql_connection.get_retirement_age_employees()
            if not results:
                self.ui.report_results_textEdit.setText("No employees of retirement age found.")
                return

            report_text = "Employees of Retirement Age with Work Experience:\n\n"
            for row in results:
                report_text += f"Name: {row['full_name']}\n" f"Age: {row['age']}\n" f"Experience: {row['experience']} years\n" "-------------------------\n"

            self.ui.report_results_textEdit.setText(report_text)

        elif selected_report == 2:
            results = self.mysql_connection.get_employees_below_average_salary()
            if not results:
                self.ui.report_results_textEdit.setText(
                    "No employees found with earnings below the department average.")
                return

            report_text = "Employees by Department with Earnings Below Average:\n\n"
            for row in results:
                report_text += (f"Department: {row['department_name']}\n"
                                f"Department Average Salary: {row['average_salary']}\n"
                                f"Name: {row['full_name']}\n"
                                f"Salary: {row['salary_amount']}\n"
                                "-------------------------\n")

            self.ui.report_results_textEdit.setText(report_text)

        elif selected_report == 3:
            department_results, company_result = self.mysql_connection.get_average_age_by_department_and_company()

            if not department_results:
                self.ui.report_results_textEdit.setText(
                    "No department data found for calculating average age."
                )
                return

            if not company_result or company_result['average_age_company'] is None:
                self.ui.report_results_textEdit.setText(
                    "No company data found for calculating average age."
                )
                return

            report_text = "Average Age of Employees in Departments:\n\n"
            for row in department_results:
                report_text += (f"Department: {row['department_name']}\n"
                                f"Average Age: {row['average_age']:.2f} years\n"
                                "-------------------------\n")

            report_text += f"\nAverage Age Across the Company: {company_result['average_age_company']:.2f} years"

            self.ui.report_results_textEdit.setText(report_text)

        elif selected_report == 4:
            total_results, monthly_results = self.mysql_connection.get_sick_leave_duration_by_department()

            if total_results and monthly_results:
                month_names = {
                    1: "January", 2: "February", 3: "March", 4: "April",
                    5: "May", 6: "June", 7: "July", 8: "August",
                    9: "September", 10: "October", 11: "November", 12: "December"
                }

                report_text = "Total Duration of Sick Leaves by Departments:\n\n"
                for row in total_results:
                    report_text += f"Department: {row['department_name']}, Total Sick Leave Duration: {row['total_leave_duration']} days\n"

                report_text += "\nMonthly Duration of Sick Leaves by Departments:\n\n"
                department_monthly_data = {}

                for row in monthly_results:
                    department_name = row['department_name']
                    month = month_names.get(row['leave_month'], f"Month {row['leave_month']}")
                    duration = row['total_leave_duration']

                    if department_name not in department_monthly_data:
                        department_monthly_data[department_name] = []

                    department_monthly_data[department_name].append((month, duration))

                for department, monthly_data in department_monthly_data.items():
                    report_text += f"\nDepartment: {department}\n"
                    monthly_data.sort(key=lambda x: list(month_names.values()).index(x[0]))
                    for month, duration in monthly_data:
                        report_text += f"  Month: {month}, Monthly Sick Leave Duration: {duration} days\n"

                self.ui.report_results_textEdit.setPlainText(report_text)
        elif selected_report == 5:
            results = self.mysql_connection.get_average_experience_by_department()
            if results:
                report_text = "Average Work Experience in Departments:\n\n"
                for row in results:
                    report_text += (f"Department: {row['department_name']}, "
                                    f"Average Experience: {row['average_experience']} years\n")
                self.ui.report_results_textEdit.setPlainText(report_text)
        elif selected_report == 6:
            department_results, company_results = self.mysql_connection.get_average_earnings_by_gender_and_department()

            if department_results and company_results:
                report_text = "Average Earnings of Men and Women by Departments:\n\n"

                current_department = None
                for row in department_results:
                    department_name = row['department_name']
                    sex = row['sex']
                    average_salary = row['average_salary']

                    if current_department != department_name:
                        report_text += f"\nDepartment: {department_name}\n"
                        current_department = department_name

                    report_text += f"  {sex}: {average_salary} UAH\n"

                report_text += "\nAverage Earnings Across the Company:\n\n"
                for row in company_results:
                    sex = row['sex']
                    average_salary_company = row['average_salary_company']
                    report_text += f"{sex}: {average_salary_company} UAH\n"

                self.ui.report_results_textEdit.setPlainText(report_text)
        else:
            self.ui.report_results_textEdit.setText("Please select a valid report option.")