from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow
from design.auth_pages import Ui_MainWindow
import sys


class AuthorizationPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.page_buttons = {
            self.ui.admin_pushButton: 1,
            self.ui.user_pushButton: 2,
            self.ui.admin_back_pushButton: 0,
            self.ui.user_back_pushButton: 0,
            self.ui.forgot_admin_pushButton: 3,
            self.ui.forgot_user_pushButton: 5,
            self.ui.login_back_pushButton: 2,
        }

        for button, page in self.page_buttons.items():
            button.clicked.connect(lambda _, p=page: self.switch_page(p))

    def switch_page(self, index):
        self.ui.stackedWidget.setCurrentIndex(index)
        print(f"Перемикання на сторінку: {index}")

        match index:
            case 1:
                self.admin_auth_page()

    def admin_auth_page(self):
        print("Do logic")


def run_application():
    app = QtWidgets.QApplication(sys.argv)
    main_window = AuthorizationPage()
    main_window.show()
    sys.exit(app.exec_())