import unittest
from unittest.mock import MagicMock, patch
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from design.edit_leave_page_main import EditLeavePage

class TestEditLeavePage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication([])

    @patch('design.edit_leave_page_main.QtWidgets.QDialog.exec_', return_value=None)
    def setUp(self, mock_exec):
        self.redis_mock = MagicMock()
        self.mysql_mock = MagicMock()

        self.worker_leaves_tableView = QtWidgets.QTableView()
        self.model = QStandardItemModel()
        self.worker_leaves_tableView.setModel(self.model)

        data = [
            ("John Doe", "Sick Leave", "2024-05-01", "2024-05-05")
        ]

        for worker_name, leave_type, start_date, end_date in data:
            row = [
                QStandardItem(worker_name),
                QStandardItem(leave_type),
                QStandardItem(start_date),
                QStandardItem(end_date)
            ]
            self.model.appendRow(row)

        self.worker_leaves_tableView.selectRow(0)

        with patch('design.edit_leave_page_main.QtWidgets.QDialog.exec_', return_value=None):
            self.edit_page = EditLeavePage(
                redis_connection=self.redis_mock,
                mysql_connection=self.mysql_mock,
                worker_leaves_tableView=self.worker_leaves_tableView
            )

        self.edit_page.ui.type_leave_comboBox.addItems(["Sick Leave", "Vacation", "Unpaid Leave"])

    def test_populate_fields(self):
        self.assertEqual(self.edit_page.ui.worker_label.text(), "John Doe")
        self.assertEqual(self.edit_page.ui.type_leave_comboBox.currentText(), "Sick Leave")
        self.assertEqual(self.edit_page.ui.start_date_dateEdit.date(), QtCore.QDate(2024, 5, 1))
        self.assertEqual(self.edit_page.ui.end_date_dateEdit.date(), QtCore.QDate(2024, 5, 5))

    def test_save_leave_request_changes_success(self):
        self.mysql_mock.get_employee_id_by_name.return_value = 1

        self.edit_page.ui.type_leave_comboBox.setCurrentText("Sick Leave")

        with patch.object(QtWidgets.QMessageBox, 'information') as mock_info:
            self.edit_page.save_leave_request_changes()
            mock_info.assert_called_once_with(
                self.edit_page.edit_leave_page,
                "Success",
                "Leave request updated successfully!"
            )

        self.mysql_mock.update_leave_request.assert_called_once_with(
            1, "Sick Leave", "2024-05-01", "2024-05-05"
        )

    @patch('design.edit_leave_page_main.QtWidgets.QMessageBox.warning')
    def test_init_without_selected_row(self, mock_warning):
        self.worker_leaves_tableView.clearSelection()

        with patch('design.edit_leave_page_main.QtWidgets.QDialog.exec_', return_value=None):
            edit_page = EditLeavePage(
                redis_connection=self.redis_mock,
                mysql_connection=self.mysql_mock,
                worker_leaves_tableView=self.worker_leaves_tableView
            )

        mock_warning.assert_called_once_with(
            edit_page.edit_leave_page, "Warning", "Please select a leave request to edit."
        )


if __name__ == '__main__':
    unittest.main()
