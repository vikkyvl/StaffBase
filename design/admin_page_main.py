from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QApplication
from design.admin_page import Ui_Form
from design.add_page_main import *


class AdminPage(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.page_buttons = {
            self.ui.manage_employees_pushButton: 1,
            self.ui.calculate_salary_pushButton: 2,
            self.ui.generate_report_pushButton: 3,
            self.ui.add_pushButton: 4,
            self.ui.exit_pushButton: 5,
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
            case 4:
                self.add_info_worker()
            case 5:
                self.confirm_exit()


    def add_info_worker(self):
        add_new_worker = AddPage()
        # add_new_worker.run()

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