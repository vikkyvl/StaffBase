import unittest
from unittest.mock import MagicMock, patch
from PyQt5 import QtWidgets
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from design.edit_personal_info_page.edit_personal_info_page_main import EditPersonalInformationPage
import sys

class TestEditPersonalInformationPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication(sys.argv)

    @classmethod
    def tearDownClass(cls):
        cls.app.quit()

    @patch('design.edit_personal_info_page.edit_personal_info_page_main.QtWidgets.QDialog.exec_', return_value=None)
    def setUp(self, mock_exec):
        self.redis_mock = MagicMock()
        self.mysql_mock = MagicMock()

        self.worker_id = "123"

        self.worker_info_tableView = QtWidgets.QTableView()
        self.model = QStandardItemModel()
        self.worker_info_tableView.setModel(self.model)

        data = [
            ("Number Of Children", "2"),
            ("Marital Status", "Married"),
            ("Phone Number", "1234567890"),
            ("Email", "johndoe@example.com"),
        ]

        for field, value in data:
            field_item = QStandardItem(field)
            value_item = QStandardItem(value)
            self.model.appendRow([field_item, value_item])

        self.edit_page = EditPersonalInformationPage(
            redis_connection=self.redis_mock,
            mysql_connection=self.mysql_mock,
            worker_id=self.worker_id,
            worker_info_tableView=self.worker_info_tableView
        )

    def test_fill_fields_from_table(self):
        self.assertEqual(self.edit_page.ui.number_of_children_spinBox.value(), 2)
        self.assertEqual(self.edit_page.ui.maritual_status_comboBox.currentText(), "Married")
        self.assertEqual(self.edit_page.ui.phone_number_lineEdit.text(), "1234567890")
        self.assertEqual(self.edit_page.ui.email_lineEdit.text(), "johndoe@example.com")

    def test_update_personal_info_success(self):
        self.mysql_mock.update_personal_info.return_value = True

        with patch.object(QtWidgets.QMessageBox, 'information') as mock_info:
            self.edit_page.update_personal_info()
            mock_info.assert_called_once_with(
                self.edit_page.edit_personal_info_page,
                "Success",
                "Personal information updated successfully!"
            )

        self.mysql_mock.update_personal_info.assert_called_once_with({
            "employee_id": self.worker_id,
            "number_of_children": 2,
            "marital_status": "Married",
            "phone_number": "1234567890",
            "email": "johndoe@example.com",
        })

    def test_update_personal_info_failure(self):
        self.mysql_mock.update_personal_info.return_value = False

        with patch.object(QtWidgets.QMessageBox, 'critical') as mock_critical:
            self.edit_page.update_personal_info()
            mock_critical.assert_called_once_with(
                self.edit_page.edit_personal_info_page,
                "Error",
                "Failed to update personal information."
            )

    def test_update_personal_info_exception(self):
        self.mysql_mock.update_personal_info.side_effect = Exception("Database error")

        with patch.object(QtWidgets.QMessageBox, 'critical') as mock_critical:
            self.edit_page.update_personal_info()
            mock_critical.assert_called_once_with(
                self.edit_page.edit_personal_info_page,
                "Error",
                "Failed to update personal information: Database error"
            )

if __name__ == '__main__':
    unittest.main()