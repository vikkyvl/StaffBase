import re
from design.edit_personal_info_page import *
from imports import *

class EditPersonalInformationPage:
    def __init__(self, redis_connection, mysql_connection, worker_id, parent=None, worker_info_tableView=None):
        self.parent = parent
        self.worker_id = worker_id
        self.worker_info_tableView = worker_info_tableView
        self.redis_connection = redis_connection
        self.mysql_connection = mysql_connection

        self.edit_personal_info_page = QtWidgets.QDialog(self.parent)
        self.edit_personal_info_page.setWindowFlags(self.edit_personal_info_page.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self.edit_personal_info_page)
        self.ui.update_pushButton.clicked.connect(self.update_personal_info)

        self.fill_fields_from_table()
        self.edit_personal_info_page.exec_()

    def fill_fields_from_table(self):
        model = self.worker_info_tableView.model()

        if model is None or model.rowCount() == 0:
            QtWidgets.QMessageBox.warning(self.edit_personal_info_page, "Warning", "No data available in the table!")
            return

        for row in range(model.rowCount()):
            field = model.index(row, 0).data()
            value = model.index(row, 1).data()

            if field == "Number Of Children":
                self.ui.number_of_children_spinBox.setValue(int(value or 0))
            elif field == "Marital Status":
                self.ui.maritual_status_comboBox.setCurrentText(value or "")
            elif field == "Phone Number":
                self.ui.phone_number_lineEdit.setText(value or "")
            elif field == "Email":
                self.ui.email_lineEdit.setText(value or "")

    def update_personal_info(self):
        number_of_children = self.ui.number_of_children_spinBox.value()
        marital_status = self.ui.maritual_status_comboBox.currentText()
        phone_number = self.ui.phone_number_lineEdit.text()
        email = self.ui.email_lineEdit.text()

        data = {
            "employee_id": self.worker_id,
            "number_of_children": number_of_children,
            "marital_status": marital_status,
            "phone_number": phone_number,
            "email": email,
        }

        try:
            success = self.mysql_connection.update_personal_info(data)

            if success:
                QtWidgets.QMessageBox.information(self.edit_personal_info_page, "Success",
                                                  "Personal information updated successfully!")
                self.edit_personal_info_page.accept()
            else:
                QtWidgets.QMessageBox.critical(self.edit_personal_info_page, "Error",
                                               "Failed to update personal information.")

        except Exception as e:
            QtWidgets.QMessageBox.critical(self.edit_personal_info_page, "Error",
                                           f"Failed to update personal information: {e}")

