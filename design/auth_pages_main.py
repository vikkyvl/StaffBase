from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow
from design.auth_pages import Ui_MainWindow
import sys


class AuthorizationPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


def run_application():
    app = QtWidgets.QApplication(sys.argv)
    main_window = AuthorizationPage()
    main_window.show()
    sys.exit(app.exec_())