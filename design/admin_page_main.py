from PyQt5 import QtWidgets
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QApplication
from design.admin_page import Ui_Form
from design.add_page_main import *

class AdminPage(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.page_buttons = {
            self.ui.manage_employees_pushButton: 1,
            self.ui.calculate_salary_pushButton: 2,
            self.ui.generate_report_pushButton: 3,
            self.ui.add_pushButton: 4,
            self.ui.exit_pushButton: 5,
            self.ui.view_pushButton: 6,
        }

        for button, page in self.page_buttons.items():
            button.clicked.connect(self.create_switch_page_handler(page))

        self.setup_worker_table()


    def create_switch_page_handler(self, page):
        def handler():
            self.switch_page(page)

        return handler


    def switch_page(self, index):
        self.ui.stackedWidget.setCurrentIndex(index)

        match index:
            case 4:
                self.add_info_worker()
            case 5:
                self.confirm_exit()
            case 6:
                self.load_workers_data()


    def add_info_worker(self):
        add_new_worker = AddPage()

    def confirm_exit(self):
        reply = QMessageBox.question(
            self,
            "Exit Confirmation",
            "Are you sure you want to exit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            QApplication.instance().quit()
        else:
            pass

    def setup_worker_table(self):
        model = QStandardItemModel()

        model.setHorizontalHeaderLabels([
            "ID", "Login", "Password", "Full Name", "Sex",
            "Department", "Position", "Hire Date", "Experience",
            "Birth Date", "Phone Number", "Marital Status", "Email"
        ])

        self.ui.worker_tableView.setModel(model)
        self.ui.worker_tableView.horizontalHeader().setStretchLastSection(True)
        self.ui.worker_tableView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.ui.worker_tableView.resizeColumnsToContents()
        self.ui.worker_tableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Interactive)

    def load_workers_data(self):
        model = self.ui.worker_tableView.model()
        model.removeRows(0, model.rowCount())

        redis_connection = Redis()
        mysql_connection = MySQL()

        redis_users = redis_connection.get_all_users()

        for user in redis_users:
            user_id = user["id"]
            login = user["login"]
            password = user["password"]

            mysql_connection.cursor.execute("""
                SELECT e.full_name, p.sex, d.department_name, pos.position_name, 
                       g.hire_date, g.experience, p.birth_date, 
                       p.phone_number, p.marital_status, p.email
                FROM Employee e
                LEFT JOIN GeneralInfo g ON e.employee_id = g.employee_id
                LEFT JOIN Departments d ON g.department_id = d.department_id
                LEFT JOIN Positions pos ON g.position_id = pos.position_id
                LEFT JOIN PersonalInfo p ON e.employee_id = p.employee_id
                WHERE e.employee_id = %s
            """, (user_id,))

            result = mysql_connection.cursor.fetchone()

            if result:
                (full_name, sex, department, position, hire_date, experience,
                 birth_date, phone_number, marital_status, email) = result

                row = [
                    user_id, login, password, full_name, sex, department,
                    position, str(hire_date), str(experience), str(birth_date),
                    phone_number if phone_number else "N/A",
                    marital_status if marital_status else "N/A",
                    email if email else "N/A"
                ]

                model.insertRow(model.rowCount())
                for col, value in enumerate(row):
                    model.setData(model.index(model.rowCount() - 1, col), value)

        self.ui.worker_tableView.resizeColumnsToContents()

