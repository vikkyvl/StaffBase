from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from design.auth_pages import Ui_MainWindow
import sys
from imports import *
from classes.authorization import *


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
            self.ui.forgot_user_pushButton: 5,
            self.ui.login_back_pushButton: 2,
            self.ui.login_admin_pushButton: 6,
            self.ui.code_continue_pushButton: 8,
        }

        self.redis_connection = Redis()
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

    def admin_auth_page(self):
        correct_password = self.redis_connection.get_admin_password()
        entered_password = self.ui.admin_password_lineEdit.text()

        if entered_password == correct_password:
            QMessageBox.information(self, "Успіх", "Вхід виконано успішно!")
        else:
            QMessageBox.warning(self, "Помилка", "Неправильний пароль!")


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
        else:
            print("Password reset cancelled.")

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
            QMessageBox.warning(self, "Помилка", "Неправильний пароль!")


def run_application():
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainPage()
    main_window.show()
    sys.exit(app.exec_())