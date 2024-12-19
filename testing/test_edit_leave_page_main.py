import unittest
from unittest.mock import MagicMock, patch
from PyQt5 import QtWidgets, QtCore
from design.edit_leave_page_main import EditLeavePage


class TestEditLeavePage(unittest.TestCase):
    @patch('design.edit_leave_page_main.QtWidgets.QMessageBox')
    def setUp(self, mock_messagebox):
        self.app = QtWidgets.QApplication([])

        # Моки для підключення до Redis і MySQL
        self.mock_redis = MagicMock()
        self.mock_mysql = MagicMock()

        # Створення мокового TableView з вибраними даними
        self.mock_table_view = MagicMock()
        self.mock_selection_model = MagicMock()
        self.mock_table_view.selectionModel.return_value = self.mock_selection_model

        # Налаштування вибраного рядка з даними
        self.mock_index = MagicMock()
        self.mock_index.row.return_value = 0

        self.mock_selection_model.selectedRows.return_value = [self.mock_index]

        # Мок для моделі, яка повертає дані
        self.mock_model = MagicMock()
        self.mock_model.index.return_value.data.side_effect = [
            "John Doe",          # Ім'я працівника
            "Sick Leave",        # Тип відпустки
            "2024-05-01",        # Дата початку
            "2024-05-05"         # Дата закінчення
        ]
        self.mock_table_view.model.return_value = self.mock_model

    def tearDown(self):
        self.app.quit()

    @patch('design.edit_leave_page_main.QtWidgets.QDialog.exec_', return_value=QtWidgets.QDialog.Accepted)
    def test_init_with_selected_row(self, mock_exec):
        # Тест на успішну ініціалізацію діалогу редагування
        with patch.object(EditLeavePage, 'populate_fields') as mock_populate:
            edit_page = EditLeavePage(self.mock_redis, self.mock_mysql, worker_leaves_tableView=self.mock_table_view)
            mock_populate.assert_called_once()
            mock_exec.assert_called_once()

    @patch('design.edit_leave_page_main.QtWidgets.QMessageBox.warning')
    def test_init_without_selected_row(self, mock_warning):
        # Тест на ініціалізацію без вибраного рядка
        self.mock_selection_model.selectedRows.return_value = []
        edit_page = EditLeavePage(self.mock_redis, self.mock_mysql, worker_leaves_tableView=self.mock_table_view)
        mock_warning.assert_called_once_with(None, "Warning", "Please select a leave request to edit.")

    @patch('design.edit_leave_page_main.QtWidgets.QMessageBox.information')
    def test_save_leave_request_changes_success(self, mock_info):
        # Тест на успішне збереження змін у заявці
        self.mock_mysql.get_employee_id_by_name.return_value = 1

        with patch.object(EditLeavePage, 'populate_fields'):
            edit_page = EditLeavePage(self.mock_redis, self.mock_mysql, worker_leaves_tableView=self.mock_table_view)
            edit_page.ui.worker_label.setText("John Doe")
            edit_page.ui.type_leave_comboBox.setCurrentText("Sick Leave")
            edit_page.ui.start_date_dateEdit.setDate(QtCore.QDate.fromString("2024-05-01", "yyyy-MM-dd"))
            edit_page.ui.end_date_dateEdit.setDate(QtCore.QDate.fromString("2024-05-05", "yyyy-MM-dd"))

            edit_page.save_leave_request_changes()

            self.mock_mysql.update_leave_request.assert_called_once_with(
                1, "Sick Leave", "2024-05-01", "2024-05-05"
            )
            mock_info.assert_called_once_with(edit_page.edit_leave_page, "Success", "Leave request updated successfully!")

    @patch('design.edit_leave_page_main.QtWidgets.QMessageBox.critical')
    def test_save_leave_request_changes_failure(self, mock_critical):
        # Тест на помилку при збереженні змін у заявці
        self.mock_mysql.get_employee_id_by_name.return_value = 1
        self.mock_mysql.update_leave_request.side_effect = Exception("Database error")

        with patch.object(EditLeavePage, 'populate_fields'):
            edit_page = EditLeavePage(self.mock_redis, self.mock_mysql, worker_leaves_tableView=self.mock_table_view)
            edit_page.ui.worker_label.setText("John Doe")
            edit_page.ui.type_leave_comboBox.setCurrentText("Sick Leave")
            edit_page.ui.start_date_dateEdit.setDate(QtCore.QDate.fromString("2024-05-01", "yyyy-MM-dd"))
            edit_page.ui.end_date_dateEdit.setDate(QtCore.QDate.fromString("2024-05-05", "yyyy-MM-dd"))

            edit_page.save_leave_request_changes()

            self.mock_mysql.update_leave_request.assert_called_once_with(
                1, "Sick Leave", "2024-05-01", "2024-05-05"
            )
            mock_critical.assert_called_once_with(
                edit_page.edit_leave_page, "Error", "Failed to update leave request: Database error"
            )


if __name__ == '__main__':
    unittest.main()
