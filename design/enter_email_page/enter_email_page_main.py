from design.enter_email_page.enter_email_page import *


class EnterEmailPage(QtWidgets.QDialog):
    def __init__(self, mysql_connection, worker_id, parent=None):
        super().__init__(parent)
        self.worker_id = worker_id
        self.mysql_connection = mysql_connection

        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.read_and_validate_email)

        self.show()

    def read_and_validate_email(self):
        email = self.ui.lineEdit.text()

        if "@" not in email or "." not in email:  # Basic email validation
            QtWidgets.QMessageBox.warning(self, "Invalid Email", "Please enter a valid email address.")
            self.ui.lineEdit.clear()
            return

        try:
            self.mysql_connection.update_user_email(self.worker_id, email)
            self.accept()
            QtWidgets.QMessageBox.information(self, "Success", "Email updated successfully!")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to update email: {e}")



