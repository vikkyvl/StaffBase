from PyQt5 import QtWidgets
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QApplication
from design.user_page import Ui_Form
from design.edit_personal_info_page_main import *
from classes.authorization import Authorization


class UserPage(QtWidgets.QWidget):
    def __init__(self, redis_connection, mysql_connection, worker_id):
        super().__init__()
        self.leave_data = None
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.redis_connection = redis_connection
        self.mysql_connection = mysql_connection
        self.worker_id = worker_id
        self.load_worker_info()

        self.page_buttons = {
            self.ui.exit_pushButton: 4,
            self.ui.my_profile_pushButton: 0,
            self.ui.salary_pushButton: 1,
            self.ui.leave_history_pushButton: 2,
            self.ui.request_leave_pushButton: 3,
            self.ui.generate_pushButton: 5,
            self.ui.send_pushButton: 6,
            self.ui.edit_pushButton: 7,
        }

        for button, page in self.page_buttons.items():
            button.clicked.connect(self.create_switch_page_handler(page))


    def create_switch_page_handler(self, page):
        def handler():
            self.switch_page(page)

        return handler


    def switch_page(self, index):
        self.ui.stackedWidget.setCurrentIndex(index)

        match index:
            case 1:
                self.load_salary_history()
            case 2:
                self.load_leave_history()
            case 4:
                self.confirm_exit()
            case 5:
                self.leave_data = self.request_leave()
            case 6:
                if self.leave_data:
                    self.send_request_leave(*self.leave_data)
            case 7:
                self.edit_personal_information()


    def edit_personal_information(self):
        edit_personal_information = EditPersonalInformationPage(redis_connection=self.redis_connection, mysql_connection=self.mysql_connection, worker_id=self.worker_id, worker_info_tableView=self.ui.worker_info_tableView)
        self.load_worker_info()

    def load_worker_info(self):
        worker_info = self.mysql_connection.get_employee_full_info(self.worker_id)
        self.ui.user_full_name_textEdit.setText(worker_info['full_name'])

        data = {
            "Department Name": worker_info["department_name"],
            "Position Name": worker_info["position_name"],
            "Hire Date": worker_info["hire_date"],
            "Total Experience": worker_info["total_experience"],
            "Birth Date": worker_info["birth_date"],
            "Sex": worker_info["sex"],
            "Number Of Children": worker_info["number_of_children"],
            "Phone Number": worker_info["phone_number"],
            "Marital Status": worker_info["marital_status"],
            "Email": worker_info["email"],
        }

        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Field", "Value"])

        for field, value in data.items():
            field_item = QStandardItem(field)
            value_item = QStandardItem(str(value) if value is not None else "")
            model.appendRow([field_item, value_item])

        self.ui.worker_info_tableView.setModel(model)
        self.ui.worker_info_tableView.resizeColumnsToContents()

        self.ui.worker_info_tableView.horizontalHeader().setStretchLastSection(True)
        self.ui.worker_info_tableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

    def request_leave(self):
        start_date_leave = self.ui.start_date_calendarWidget.selectedDate().toString('yyyy-MM-dd')
        end_date_leave = self.ui.end_date_calendarWidget.selectedDate().toString('yyyy-MM-dd')
        leave_type = self.ui.type_leave_comboBox.currentText()

        if not leave_type:
            QMessageBox.warning(self, "Error", "Leave type cannot be empty.")
            return None

        if start_date_leave > end_date_leave:
            QMessageBox.warning(self, "Error", "Start date cannot be later than end date.")
            return None

        worker_info = self.mysql_connection.get_info_for_request(self.worker_id)

        if worker_info:
            full_name = worker_info["full_name"]
            company_name = worker_info["company_name"]
            email = worker_info["email"]

            body = (
                f"Dear {company_name},\n\n"
                f"I, {full_name}, kindly request approval for {leave_type.lower()} "
                f"from {start_date_leave} to {end_date_leave}.\n\n"
                f"If necessary, I can provide additional information or supporting documents. "
                f"Thank you for your consideration.\n\n"
                f"Sincerely,\n"
                f"{full_name}\n"
                f"Contact Info: {email}"
            )

            self.ui.generate_text_textEdit.setText(body)
            return full_name, leave_type, body

        QMessageBox.warning(self, "Error", "Worker information not found.")
        return None

    def send_request_leave(self, full_name, leave_type, body):
        try:
            email_transaction = Authorization()
            email_transaction.send_leave_request_email(full_name, leave_type, body)
            self.ui.generate_text_textEdit.clear()
            QtWidgets.QMessageBox.information(self, "Success", "Leave request email sent successfully!")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to send leave request email: {e}")


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

    def load_salary_history(self):
        salary_history = self.mysql_connection.get_salary_history(self.worker_id)

        if not salary_history:
            QtWidgets.QMessageBox.warning(self, "Warning", "No salary history found for this employee.")
            return

        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Date", "Salary"])

        for record in salary_history:
            date_item = QStandardItem(record["salary_month"])
            salary_item = QStandardItem(f"{record['salary_amount']:.2f}")
            model.appendRow([date_item, salary_item])

        self.ui.salary_history_tableView.setModel(model)
        self.ui.salary_history_tableView.resizeColumnsToContents()

        self.ui.salary_history_tableView.horizontalHeader().setStretchLastSection(True)
        self.ui.salary_history_tableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

    def load_leave_history(self):
        try:
            leaves = self.mysql_connection.get_leaves_history(self.worker_id)

            if not leaves:
                QtWidgets.QMessageBox.warning(self, "Warning", "No leave history found for this employee.")
                return

            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(["Type", "Start Date", "End Date", "Duration"])

            for leave in leaves:
                type_item = QStandardItem(leave["leave_type"])
                start_date_item = QStandardItem(str(leave["start_date"]))
                end_date_item = QStandardItem(str(leave["end_date"]))
                duration_item = QStandardItem(str(leave["duration"]))

                model.appendRow([type_item, start_date_item, end_date_item, duration_item])

            self.ui.leave_history_tableView.setModel(model)
            self.ui.leave_history_tableView.resizeColumnsToContents()
            self.ui.leave_history_tableView.horizontalHeader().setStretchLastSection(True)
            self.ui.leave_history_tableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load leave history: {e}")