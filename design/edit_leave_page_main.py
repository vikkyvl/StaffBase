import re
from design.edit_leave_page import *
from imports import *

class EditLeavePage:
    def __init__(self, redis_connection, mysql_connection, parent=None, worker_leaves_tableView=None):
        self.parent = parent
        self.worker_leaves_tableView = worker_leaves_tableView
        self.redis_connection = redis_connection
        self.mysql_connection = mysql_connection

        self.edit_leave_page = QtWidgets.QDialog(self.parent)
        self.edit_leave_page.setWindowFlags(self.edit_leave_page.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self.edit_leave_page)

        self.edit_leave_page.exec_()