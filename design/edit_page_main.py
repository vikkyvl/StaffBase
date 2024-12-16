import re
from design.edit_page import *
from imports import *

class EditPage():
    def __init__(self, parent=None):
        self.parent = parent
        self.edit_page = QtWidgets.QDialog(self.parent)
        self.edit_page.setWindowFlags(self.edit_page.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self.edit_page)

        self.edit_page.exec_()