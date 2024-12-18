from PyQt5 import QtWidgets
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QApplication
from design.user_page import Ui_Form
from classes.authorization import Authorization


class UserPage(QtWidgets.QWidget):
    def __init__(self, redis_connection, mysql_connection, worker_id):
        super().__init__()
        self.leave_data = None
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.page_buttons = {
            self.ui.exit_pushButton: 4,
            self.ui.my_profile_pushButton: 0,
            self.ui.salary_pushButton: 1,
            self.ui.leave_history_pushButton: 2,
            self.ui.request_leave_pushButton: 3,
            self.ui.generate_pushButton: 5,
            self.ui.send_pushButton: 6,
        }

        self.redis_connection = redis_connection
        self.mysql_connection = mysql_connection
        self.worker_id = worker_id

        for button, page in self.page_buttons.items():
            button.clicked.connect(self.create_switch_page_handler(page))


    def create_switch_page_handler(self, page):
        def handler():
            self.switch_page(page)

        return handler


    def switch_page(self, index):
        self.ui.stackedWidget.setCurrentIndex(index)

        match index:
            case 4:
                self.confirm_exit()
            case 5:
                self.leave_data = self.request_leave()
            case 6:
                if self.leave_data:
                    self.send_request_leave(*self.leave_data)

    # def load_worker_info(self):


    def request_leave(self):
        start_date_leave = self.ui.start_date_calendarWidget.selectedDate().toString('yyyy-MM-dd')
        end_date_leave = self.ui.end_date_calendarWidget.selectedDate().toString('yyyy-MM-dd')
        leave_type = self.ui.type_leave_comboBox.currentText()
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