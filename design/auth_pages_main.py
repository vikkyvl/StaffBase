from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow
from auth_pages import Ui_MainWindow


class AuthorizationPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main_window = AuthorizationPage()
    main_window.show()
    sys.exit(app.exec_())