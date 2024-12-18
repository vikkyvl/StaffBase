import re
from design.edit_leave_page import *
from imports import *

class EditLeavePage:
    def __init__(self, redis_connection, mysql_connection, parent=None, worker_leaves_tableView=None):
        self.parent = parent
        self.worker_leaves_tableView = worker_leaves_tableView
        self.redis_connection = redis_connection
        self.mysql_connection = mysql_connection

        selected_row = self.worker_leaves_tableView.currentIndex().row()
        if selected_row == -1:
            QtWidgets.QMessageBox.warning(None, "Warning", "Please select a leave request to edit.")
            return

        self.edit_leave_page = QtWidgets.QDialog(self.parent)
        self.edit_leave_page.setWindowFlags(self.edit_leave_page.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self.edit_leave_page)

        self.populate_fields()

        self.ui.pushButton.clicked.connect(self.save_leave_request_changes)

        self.edit_leave_page.exec_()

    def populate_fields(self):
        selected_indexes = self.worker_leaves_tableView.selectionModel().selectedRows()
        if not selected_indexes:
            QtWidgets.QMessageBox.warning(self.edit_leave_page, "Warning", "No leave request selected.")
            self.edit_leave_page.reject()
            return

        selected_row = selected_indexes[0].row()
        model = self.worker_leaves_tableView.model()

        worker_name = model.index(selected_row, 0).data()
        leave_type = model.index(selected_row, 1).data()
        start_date = model.index(selected_row, 2).data()
        end_date = model.index(selected_row, 3).data()

        self.ui.worker_label.setText(worker_name)
        self.ui.type_leave_comboBox.setCurrentText(leave_type)
        self.ui.start_date_dateEdit.setDate(QtCore.QDate.fromString(start_date, "yyyy-MM-dd"))
        self.ui.end_date_dateEdit.setDate(QtCore.QDate.fromString(end_date, "yyyy-MM-dd"))

    def save_leave_request_changes(self):
        worker_name = self.ui.worker_label.text()
        leave_type = self.ui.type_leave_comboBox.currentText()
        start_date = self.ui.start_date_dateEdit.date().toString("yyyy-MM-dd")
        end_date = self.ui.end_date_dateEdit.date().toString("yyyy-MM-dd")

        employee_id = self.mysql_connection.get_employee_id_by_name(worker_name)

        try:
            self.mysql_connection.update_leave_request(employee_id, leave_type, start_date, end_date)
            QtWidgets.QMessageBox.information(self.edit_leave_page, "Success", "Leave request updated successfully!")
            self.edit_leave_page.accept()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.edit_leave_page, "Error", f"Failed to update leave request: {e}")
