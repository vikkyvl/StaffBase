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
        }

        self.redis_connection = Redis()
        self.auth_process = Authorization()

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
            self.ui.stackedWidget.setCurrentIndex(3)
            admin_email = self.redis_connection.get_email()
            self.auth_process.change_password(admin_email)
            self.ui.email_textEdit.setHtml(f"<div style='text-align: center;'><b>{admin_email}</b>.</div>")
            print("Password reset confirmed. Navigating to page 3.")
        else:
            print("Password reset cancelled.")


def run_application():
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainPage()
    main_window.show()
    sys.exit(app.exec_())