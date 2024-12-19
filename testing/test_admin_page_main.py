import unittest
from unittest.mock import MagicMock, patch
from PyQt5 import QtWidgets, QtCore
from design.admin_page.admin_page_main import AdminPage


class TestAdminPage(unittest.TestCase):
    @patch('design.admin_page.admin_page_main.Redis')
    @patch('design.admin_page.admin_page_main.MySQL')
    def setUp(self, mock_redis, mock_mysql):
        self.app = QtWidgets.QApplication([])

        self.mock_redis = mock_redis.return_value
        self.mock_mysql = mock_mysql.return_value

        self.mock_redis.get_all_users.return_value = [
            {"id": 1, "login": "john_doe", "password": "Password123!"}
        ]
        self.mock_mysql.get_worker_details.return_value = (
            "John Doe", "Male", "Finance", "Manager", "2023-04-27",
            "3", "5", "1990-01-01", "123456789", "Single", "john@example.com"
        )

        self.admin_page = AdminPage(self.mock_redis, self.mock_mysql)

    def tearDown(self):
        self.app.quit()

    def test_switch_page_calls_correct_method(self):
        with patch.object(self.admin_page, 'add_info_worker') as mock_add_info_worker, \
                patch.object(self.admin_page, 'confirm_exit') as mock_confirm_exit, \
                patch.object(self.admin_page, 'load_workers_data') as mock_load_workers_data, \
                patch.object(self.admin_page, 'delete_workers_data') as mock_delete_workers_data, \
                patch.object(self.admin_page, 'edit_info_worker') as mock_edit_info_worker:
            self.admin_page.switch_page(4)
            mock_add_info_worker.assert_called_once()

            self.admin_page.switch_page(5)
            mock_confirm_exit.assert_called_once()

            self.admin_page.switch_page(6)
            mock_load_workers_data.assert_called_once()

            self.admin_page.switch_page(7)
            mock_delete_workers_data.assert_called_once()

            self.admin_page.switch_page(8)
            mock_edit_info_worker.assert_called_once()

    def test_add_info_worker_calls_AddPage(self):
        with patch('design.admin_page.admin_page_main.AddPage') as mock_add_page:
            self.admin_page.add_info_worker()
            mock_add_page.assert_called_once_with(
                redis_connection=self.mock_redis, mysql_connection=self.mock_mysql
            )

    def test_edit_info_worker_calls_EditPage(self):
        with patch('design.admin_page.admin_page_main.EditPage') as mock_edit_page:
            self.admin_page.edit_info_worker()
            mock_edit_page.assert_called_once_with(
                redis_connection=self.mock_redis, mysql_connection=self.mock_mysql,
                worker_table=self.admin_page.ui.worker_tableView
            )

    def test_confirm_exit_calls_QApplication_quit_on_yes(self):
        with patch('PyQt5.QtWidgets.QMessageBox.question', return_value=QtWidgets.QMessageBox.Yes), \
                patch('PyQt5.QtWidgets.QApplication.quit') as mock_quit:
            self.admin_page.confirm_exit()
            mock_quit.assert_called_once()

    def test_delete_workers_data_calls_delete_methods(self):
        self.admin_page.ui.worker_tableView.selectionModel = MagicMock()
        selected_indexes = [MagicMock()]
        self.admin_page.ui.worker_tableView.selectionModel().selectedRows.return_value = selected_indexes

        mock_model = MagicMock()
        self.admin_page.ui.worker_tableView.model = MagicMock(return_value=mock_model)
        mock_index = MagicMock()
        mock_model.index.return_value = mock_index
        mock_index.data.return_value = "1"

        with patch('PyQt5.QtWidgets.QMessageBox.question', return_value=QtWidgets.QMessageBox.Yes), \
                patch('PyQt5.QtWidgets.QMessageBox.information') as mock_info:
            self.admin_page.delete_workers_data()
            self.mock_mysql.delete_worker_by_id.assert_called_once_with("1")
            self.mock_redis.delete_employee.assert_called_once()
            mock_info.assert_called_once_with(self.admin_page, "Success", "Worker '1' has been successfully deleted.")

    def test_load_workers_data_populates_table(self):
        model = self.admin_page.ui.worker_tableView.model()
        self.admin_page.load_workers_data()
        self.assertEqual(model.rowCount(), 1)
        self.assertEqual(model.index(0, 1).data(), "john_doe")

    def test_load_workers_into_combobox(self):
        self.mock_mysql.get_all_workers.return_value = [
            (1, "John Doe"),
            (2, "Jane Smith"),
        ]

        self.admin_page.load_workers_into_combobox()

        self.assertEqual(self.admin_page.ui.worker_salary_comboBox.count(), 2)
        self.assertEqual(self.admin_page.ui.worker_leave_comboBox.count(), 2)

    def test_add_leave_request_success(self):
        self.admin_page.ui.worker_leave_comboBox.addItem("John Doe", 1)
        self.admin_page.ui.worker_leave_comboBox.setCurrentIndex(0)

        self.admin_page.ui.type_leave_comboBox.addItem("Sick")
        self.admin_page.ui.type_leave_comboBox.setCurrentIndex(1)

        start_date = QtCore.QDate(2024, 5, 1)
        end_date = QtCore.QDate(2024, 5, 5)

        self.admin_page.ui.start_date_dateEdit.setDate(start_date)
        self.admin_page.ui.end_date_dateEdit.setDate(end_date)

        self.mock_mysql.get_employee_id_by_name.return_value = 1
        self.mock_mysql.add_leave_request.return_value = None

        with patch.object(QtWidgets.QMessageBox, 'information') as mock_info:
            self.admin_page.add_leave_request()
            self.mock_mysql.get_employee_id_by_name.assert_called_once_with("John Doe")
            self.mock_mysql.add_leave_request.assert_called_once_with(
                1, "Sick", "2024-05-01", "2024-05-05"
            )
            mock_info.assert_called_once_with(
                self.admin_page, "Success", "Leave request added successfully!"
            )

    def test_view_leave_requests(self):
        self.mock_mysql.get_all_leave_requests.return_value = [
            ("John Doe", "Sick Leave", "2024-05-01", "2024-05-05", 5)
        ]

        self.admin_page.view_leave_requests()

        model = self.admin_page.ui.worker_leaves_tableView.model()
        self.assertEqual(model.rowCount(), 1)
        self.assertEqual(model.index(0, 0).data(), "John Doe")
        self.assertEqual(model.index(0, 1).data(), "Sick Leave")

    def test_save_leave_request_changes(self):
        self.admin_page.ui.worker_leaves_tableView.selectionModel = MagicMock()
        selected_indexes = [MagicMock()]
        self.admin_page.ui.worker_leaves_tableView.selectionModel().selectedRows.return_value = selected_indexes

        mock_model = MagicMock()
        self.admin_page.ui.worker_leaves_tableView.model = MagicMock(return_value=mock_model)

        mock_index = MagicMock()
        mock_model.index.return_value = mock_index
        mock_index.data.side_effect = [
            "John Doe",
            "Sick Leave",
            "2024-05-01",
            "2024-05-05"
        ]

        self.mock_mysql.get_employee_id_by_name.return_value = 1

        with patch.object(QtWidgets.QMessageBox, 'information') as mock_info:
            self.admin_page.save_leave_request_changes()
            mock_info.assert_called_once_with(
                self.admin_page, "Success", "Leave request updated successfully!"
            )
            self.mock_mysql.update_leave_request.assert_called_once_with(1, "Sick Leave", "2024-05-01", "2024-05-05")

    def test_delete_leave_request(self):
        self.admin_page.ui.worker_leaves_tableView.selectionModel = MagicMock()
        selected_indexes = [MagicMock()]
        self.admin_page.ui.worker_leaves_tableView.selectionModel().selectedRows.return_value = selected_indexes

        mock_model = MagicMock()
        self.admin_page.ui.worker_leaves_tableView.model = MagicMock(return_value=mock_model)

        mock_index = MagicMock()
        mock_model.index.return_value = mock_index
        mock_index.data.side_effect = [
            "John Doe",
            "Sick Leave",
            "2024-05-01",
            "2024-05-05"
        ]

        self.mock_mysql.get_employee_id_by_name.return_value = 1

        with patch.object(QtWidgets.QMessageBox, 'question', return_value=QtWidgets.QMessageBox.Yes), \
                patch.object(QtWidgets.QMessageBox, 'information') as mock_info:
            self.admin_page.delete_leave_request()
            mock_info.assert_called_once_with(
                self.admin_page, "Success", "Leave request deleted successfully!"
            )
            self.mock_mysql.delete_leave_request.assert_called_once_with(1, "Sick Leave", "2024-05-01", "2024-05-05")
            mock_model.removeRow.assert_called_once_with(selected_indexes[0].row())

    def test_calculate_salary_invalid_premium(self):
        self.admin_page.ui.worker_salary_comboBox.addItem("John Doe", 1)
        self.admin_page.ui.worker_salary_comboBox.setCurrentIndex(0)
        self.admin_page.ui.premium_lineEdit.setText("")

        with patch.object(QtWidgets.QMessageBox, 'critical') as mock_critical:
            self.admin_page.calculate_salary()
            mock_critical.assert_called_once_with(
                self.admin_page, "Error", "Please fill in all required fields."
            )

if __name__ == '__main__':
    unittest.main()