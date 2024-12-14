from design.add_page import *

class AddPage:
    def __init__(self, parent=None):
        self.parent = parent
        self.add_page = QtWidgets.QDialog(self.parent)
        self.add_page.setWindowFlags(self.add_page.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self.add_page)
        self.add_page.exec_()

    def add_date(self):
        employee_login = self.ui.login_lineEdit.text()
        employee_password = self.ui.password_lineEdit.text()
        employee_full_name = self.ui.full_name_lineEdit.text()
        employee_sex = self.ui.sex_comboBox.currentText()

