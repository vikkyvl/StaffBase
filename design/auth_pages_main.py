from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from design.auth_pages import Ui_MainWindow
from design.admin_page_main import AdminPage
from classes.authorization import Authorization
import sys
from imports import *


class MainPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.page_buttons = {
            self.ui.admin_pushButton: 1,
            self.ui.user_pushButton: 2,
            self.ui.admin_back_pushButton: 0,
            self.ui.user_back_pushButton: 0,
            self.ui.forgot_admin_pushButton: 7,
            self.ui.forgot_user_pushButton: 10,
            self.ui.login_back_pushButton: 2,
            self.ui.login_admin_pushButton: 6,
            self.ui.code_continue_pushButton: 8,
            self.ui.login_user_pushButton: 9
        }

        self.redis_connection = Redis()
        self.mysql_connection = MySQL()
        self.auth_process = Authorization()

        self.verification_code = None
        self.combined_code = None

        for button, page in self.page_buttons.items():
            button.clicked.connect(self.create_switch_page_handler(page))

    def create_switch_page_handler(self, page):
        def handler():
            self.switch_page(page)

        return handler

    def switch_page(self, index):
        self.ui.stackedWidget.setCurrentIndex(index)
        print(f"Перемикання на сторінку: {index}")

        match index:
            case 6:
                self.admin_auth_page()
            case 7:
                self.admin_send_code_page()
            case 8:
                self.check_code()
            case 9:
                self.user_auth_page()
            case 10:
                self.open_user_login()

    def open_admin_page(self):
        self.close()
        self.admin_page = AdminPage(redis_connection=self.redis_connection,mysql_connection=self.mysql_connection)
        self.admin_page.show()

    def admin_auth_page(self):
        correct_password = self.redis_connection.get_admin_password()
        entered_password = self.ui.admin_password_lineEdit.text()

        if entered_password == correct_password:
            self.open_admin_page()
        else:
            QMessageBox.warning(self, "Error", "Incorrect password. Please try again or click 'Forgot your password'.")
            self.ui.admin_password_lineEdit.clear()

    def user_auth_page(self):
        entered_login = self.ui.user_login_lineEdit.text()
        entered_password = self.ui.user_password_lineEdit.text()

        existence_user = self.redis_connection.is_exist_user(entered_login)

        if existence_user == 1:
            correct_password = self.redis_connection.get_password_by_login(entered_login)
            if correct_password == entered_password:
                pass
            else:
                QMessageBox.warning(self, "Error", "Incorrect password. Please try again or click 'Forgot your password'.")
        else:
            QMessageBox.warning(
                self,
                "Error",
                "This user does not exist. Please contact the administrator or check the login you entered."
            )
            self.ui.user_login_lineEdit.clear()
            self.ui.user_password_lineEdit.clear()

    def admin_send_code_page(self):
        reply = QMessageBox.question(
            self,
            "Confirm Action",
            "Are you sure you want to reset the password?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            admin_email = self.redis_connection.get_email()
            self.verification_code = self.auth_process.send_code(admin_email)
            self.ui.email_textEdit.setHtml(f"<div style='text-align: center;'><b>{admin_email}</b>.</div>")
            self.ui.stackedWidget.setCurrentIndex(3)
            self.ui.reset_password_pushButton.clicked.connect(self.admin_reset_password)

    def admin_reset_password(self):
        entered_new_password = self.ui.new_password_lineEdit.text()
        entered_confirmation_new_password = self.ui.confirm_new_password_lineEdit.text()

        if entered_new_password == entered_confirmation_new_password:
            self.redis_connection.set_new_admin_password(entered_new_password)
            QMessageBox.information(self, "Success", "Password has been successfully reset.")
            self.ui.stackedWidget.setCurrentIndex(1)
        else:
            QMessageBox.warning(self, "Error", "Passwords do not match. Please try again.")
            self.ui.new_password_lineEdit.clear()
            self.ui.confirm_new_password_lineEdit.clear()

    def check_code(self):
        line_edits = [
            self.ui.first_n_lineEdit,
            self.ui.second_n_lineEdit,
            self.ui.third_n_lineEdit,
            self.ui.fourth_n_lineEdit,
            self.ui.fifth_n_lineEdit,
            self.ui.sixth_n_lineEdit
        ]
        self.combined_code = "".join([line_edit.text().strip() for line_edit in line_edits])

        if self.verification_code == self.combined_code:
            self.ui.stackedWidget.setCurrentIndex(4)
        else:
            choice = QMessageBox.warning(
                self,
                "Error",
                "Incorrect code! Would you like to try again or return to the main page?",
                QMessageBox.Retry | QMessageBox.Cancel
            )
            if choice == QMessageBox.Retry:
                self.clear_line_edits(line_edits)
            elif choice == QMessageBox.Cancel:
                self.clear_line_edits(line_edits)
                self.ui.stackedWidget.setCurrentIndex(0)

    def clear_line_edits(self, line_edits):
        for line_edit in line_edits:
            line_edit.clear()

    def open_user_login(self):
        reply = QMessageBox.question(
            self,
            "Confirm Action",
            "Are you sure you want to reset the password?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.ui.stackedWidget.setCurrentIndex(5)
            self.ui.continue_rec_pushButton.clicked.connect(self.handle_continue_rec)

    def handle_continue_rec(self):
        user_login = self.ui.login_for_pass_lineEdit.text()
        existing_user = self.redis_connection.is_exist_user(user_login)
        if existing_user:
            user_id = self.redis_connection.get_id_by_login(user_login)
            user_email = self.mysql_connection.get_email_by_id(user_id)
            if user_email:
                self.ui.stackedWidget.setCurrentIndex(3)
                self.user_send_code_page(user_login, user_email)
            else:
                QMessageBox.warning(
                    self,
                    "No Email Found",
                    "Sorry, you do not have an email associated with your account to reset the password. Please contact the administrator."
                )
                self.ui.login_for_pass_lineEdit.clear()
                self.ui.stackedWidget.setCurrentIndex(0)
        else:
            self.ui.login_for_pass_lineEdit.clear()
            QMessageBox.warning(
                self,
                "User Not Found",
                "The user does not exist, or you have entered an incorrect login. Please try again."
            )

    def user_send_code_page(self, user_login, user_email):
        self.verification_code = self.auth_process.send_code(user_email)
        self.ui.email_textEdit.setHtml(f"<div style='text-align: center;'><b>{user_email}</b>.</div>")
        self.ui.stackedWidget.setCurrentIndex(3)
        self.ui.reset_password_pushButton.clicked.connect(lambda: self.user_reset_password(user_login))

    def user_reset_password(self, user_login):
        entered_new_password = self.ui.new_password_lineEdit.text()
        entered_confirmation_new_password = self.ui.confirm_new_password_lineEdit.text()

        if entered_new_password == entered_confirmation_new_password:
            self.redis_connection.update_employee_password(user_login, entered_new_password)
            QMessageBox.information(self, "Success", "Password has been successfully reset.")
            self.ui.stackedWidget.setCurrentIndex(2)
        else:
            QMessageBox.warning(self, "Error", "Passwords do not match. Please try again.")
            self.ui.new_password_lineEdit.clear()
            self.ui.confirm_new_password_lineEdit.clear()

def run_application():
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainPage()
    main_window.show()
    sys.exit(app.exec_())