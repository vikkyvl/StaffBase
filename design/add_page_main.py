from design.add_page import *

class AddPage:
    def __init__(self, parent=None):
        self.parent = parent
        self.add_page = QtWidgets.QDialog(self.parent)
        self.add_page.setWindowFlags(self.add_page.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self.add_page)

    def run(self):
        self.add_page.exec_()