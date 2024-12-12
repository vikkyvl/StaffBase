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
    def create_tables(self):
        tables = {
            "Employee": """
                CREATE TABLE IF NOT EXISTS Employee (
                    employee_id VARCHAR(36) PRIMARY KEY,
                    full_name VARCHAR(255)
                )
            """,
            "GeneralInfo": """
                CREATE TABLE IF NOT EXISTS GeneralInfo (
                    employee_id VARCHAR(36),
                    department_id VARCHAR(36),
                    position_id VARCHAR(36),
                    hire_date DATE,
                    experience INT,
                    PRIMARY KEY (employee_id),
                    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id)
                )
            """,
            "PersonalInfo": """
                CREATE TABLE IF NOT EXISTS PersonalInfo (
                    employee_id VARCHAR(36),
                    birth_date DATE,
                    sex VARCHAR(10),
                    number_of_children INT,
                    phone_number VARCHAR(15),
                    marital_status VARCHAR(20),
                    email VARCHAR(255),
                    PRIMARY KEY (employee_id),
                    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id)
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