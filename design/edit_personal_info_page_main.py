import re
from design.edit_personal_info_page import *
from imports import *

class EditPersonalInformationPage:
    def __init__(self, redis_connection, mysql_connection, parent=None, worker_info_tableView=None):
        self.parent = parent
        self.worker_info_tableView = worker_info_tableView
        self.redis_connection = redis_connection
        self.mysql_connection = mysql_connection

        self.edit_personal_info_page = QtWidgets.QDialog(self.parent)
        self.edit_personal_info_page.setWindowFlags(self.edit_personal_info_page.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self.edit_personal_info_page)
        # self.ui.update_pushButton.clicked.connect(self.update_employee_personal_info())

        self.edit_personal_info_page.exec_()



