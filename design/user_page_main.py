from PyQt5 import QtWidgets
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QApplication
from design.user_page import Ui_Form


class UserPage(QtWidgets.QWidget):
    def __init__(self, redis_connection, mysql_connection):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.page_buttons = {
            self.ui.exit_pushButton: 4,
            self.ui.my_profile_pushButton: 0,
            self.ui.salary_pushButton: 1,
            self.ui.leave_history_pushButton: 2,
            self.ui.request_leave_pushButton: 3,
        }

        self.redis_connection = redis_connection
        self.mysql_connection = mysql_connection

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