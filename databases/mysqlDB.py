import mysql.connector
from classes.employee import Employee
from classes.general_info import GeneralInfo
from classes.personal_info import PersonalInfo

class MySQL:
    def __init__(self, host="localhost", port=3306, user="root", password="root-pw", database="staff_base", use_pure=True):
            self.mydb = mysql.connector.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                use_pure=use_pure
            )
            self.cursor = self.mydb.cursor()
            self.create_tables()

    def create_tables(self):
        tables = {
            "Employee": """
                CREATE TABLE IF NOT EXISTS Employee (
                    employee_id VARCHAR(36) PRIMARY KEY,
                    full_name VARCHAR(255) NOT NULL
                )
            """,
            "Departments": """
                CREATE TABLE IF NOT EXISTS Departments (
                    department_id INT PRIMARY KEY AUTO_INCREMENT,
                    department_name VARCHAR(255) NOT NULL,
                    department_positions INT DEFAULT 0
                )
            """,
            "Positions": """
                CREATE TABLE IF NOT EXISTS Positions (
                    position_id INT PRIMARY KEY AUTO_INCREMENT,
                    department_id INT NOT NULL,
                    position_name VARCHAR(255) NOT NULL,
                    salary_amount DECIMAL(10, 2) NOT NULL,
                    FOREIGN KEY (department_id) REFERENCES Departments(department_id) ON DELETE CASCADE
                )
            """,
            "Company": """
                CREATE TABLE IF NOT EXISTS Company (
                    company_name VARCHAR(255) PRIMARY KEY,
                    num_of_departments INT DEFAULT 0
                )
            """,
            "GeneralInfo": """
                CREATE TABLE IF NOT EXISTS GeneralInfo (
                    employee_id VARCHAR(36) PRIMARY KEY,
                    department_id INT NOT NULL,
                    position_id INT NOT NULL,
                    hire_date DATE NOT NULL,
                    experience INT,
                    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id) ON DELETE CASCADE,
                    FOREIGN KEY (department_id) REFERENCES Departments(department_id),
                    FOREIGN KEY (position_id) REFERENCES Positions(position_id)
                )
            """,
            "PersonalInfo": """
                CREATE TABLE IF NOT EXISTS PersonalInfo (
                    employee_id VARCHAR(36) PRIMARY KEY,
                    birth_date DATE NOT NULL,
                    sex ENUM('Male', 'Female'),
                    number_of_children INT DEFAULT 0,
                    phone_number VARCHAR(15),
                    marital_status ENUM('Single', 'Married'),
                    email VARCHAR(255) UNIQUE,
                    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id) ON DELETE CASCADE
                )
            """,
            "Salary": """
                CREATE TABLE IF NOT EXISTS Salary (
                    employee_id VARCHAR(36),
                    salary_month DATE NOT NULL,
                    salary_amount DECIMAL(10, 2) NOT NULL,
                    PRIMARY KEY (employee_id, salary_month),
                    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id) ON DELETE CASCADE
                )
            """,
            "Leaves": """
                CREATE TABLE IF NOT EXISTS Leaves (
                    leave_id INT AUTO_INCREMENT PRIMARY KEY,
                    employee_id VARCHAR(36) NOT NULL,
                    leave_type ENUM('Sick', 'Vacation', 'Time Off') NOT NULL,
                    start_date DATE NOT NULL,
                    end_date DATE NOT NULL,
                    duration INT GENERATED ALWAYS AS (DATEDIFF(end_date, start_date) + 1),
                    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id) ON DELETE CASCADE
                )
            """
        }

        for table_name, table_query in tables.items():
            try:
                self.cursor.execute(table_query)
                print(f"Таблиця '{table_name}' створена успішно.")
            except mysql.connector.Error as e:
                print(f"Помилка під час створення таблиці '{table_name}':", e)

        self.mydb.commit()

    def add_employee(self, employee: Employee):
        cursor = self.mydb.cursor()
        query = "INSERT INTO Employee (ID, full_name) VALUES (%s, %s)"
        cursor.execute(query, (employee._employee_id, employee._full_name))
        self.mydb.commit()
        cursor.close()

    def add_general_info(self, general_info: GeneralInfo):
        cursor = self.mydb.cursor()
        query = """INSERT INTO General_Info (ID, ID_Department, ID_Position, hire_date, experience)
                   VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(query, (general_info._employee_id, general_info._department_id, general_info._position_id, general_info._hire_date, general_info._experience))
        self.mydb.commit()
        cursor.close()

    def add_personal_info(self, personal_info: PersonalInfo):
        cursor = self.mydb.cursor()
        query = """INSERT INTO Personal_Info (ID, birth_date, sex, number_of_children, phone_number, marital_status, email)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(query, (personal_info._employee_id, personal_info._birth_date, personal_info._sex, personal_info._number_of_children, personal_info._phone_number, personal_info._marital_status, personal_info._email))
        self.mydb.commit()
        cursor.close()

    def get_email_by_id(self, employee_id):
        query = "SELECT email FROM PersonalInfo WHERE employee_id = %s"
        self.cursor.execute(query, (employee_id,))
        result = self.cursor.fetchone()

        return result[0] if result and "@" in result[0] else 0