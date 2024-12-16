import json
import mysql.connector
from classes.department import Department
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
            self.check_and_insert_departments()
            self.create_trigger_calculate_experience_generalinfo()

    def __del__(self):
        try:
            if self.cursor:
                self.cursor.close()
            if self.mydb:
                self.mydb.close()
        except Exception as e:
            print(f"Error while closing resources: {e}")

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
                    previous_experience INT DEFAULT 0,
                    total_experience INT DEFAULT 0,
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
                print(f"Table '{table_name}' is successfully created.")
            except mysql.connector.Error as e:
                print(f"Error while creating table '{table_name}':", e)

        self.mydb.commit()

    def add_employee(self, employee: Employee):
        cursor = self.mydb.cursor()
        query = "INSERT INTO Employee (employee_id, full_name) VALUES (%s, %s)"
        cursor.execute(query, (employee.get_employee_ID(), employee.get_full_name()))
        self.mydb.commit()
        cursor.close()

    def add_general_info(self, general_info: GeneralInfo):
        cursor = self.mydb.cursor()
        query = """INSERT INTO GeneralInfo (employee_id, department_id, position_id, hire_date, previous_experience)
                   VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(
            query,(general_info.get_employee_id(), general_info.get_department_id(), general_info.get_position_id(), general_info.get_hire_date(),general_info.get_experience())
        )
        self.mydb.commit()
        cursor.close()

    def add_personal_info(self, personal_info: PersonalInfo):
        cursor = self.mydb.cursor()
        query = """INSERT INTO PersonalInfo (employee_id, birth_date, sex, number_of_children, phone_number, marital_status, email)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(
            query,( personal_info.get_employee_id(), personal_info.get_birth_date(), personal_info.get_sex(), personal_info.get_number_of_children(), personal_info.get_phone_number(), personal_info.get_marital_status(), personal_info.get_email())
        )
        self.mydb.commit()
        cursor.close()

    def get_worker_details(self, employee_id):
        query = """
            SELECT e.full_name, p.sex, d.department_name, pos.position_name, 
                   g.hire_date, g.previous_experience, g.total_experience, p.birth_date, 
                   p.phone_number, p.marital_status, p.email
            FROM Employee e
            LEFT JOIN GeneralInfo g ON e.employee_id = g.employee_id
            LEFT JOIN Departments d ON g.department_id = d.department_id
            LEFT JOIN Positions pos ON g.position_id = pos.position_id
            LEFT JOIN PersonalInfo p ON e.employee_id = p.employee_id
            WHERE e.employee_id = %s
        """
        self.cursor.execute(query, (employee_id,))
        return self.cursor.fetchone()

    def delete_worker_by_id(self, employee_id):
        delete_query = "DELETE FROM Employee WHERE employee_id = %s"
        self.cursor.execute(delete_query, (employee_id,))
        self.mydb.commit()
        print(f"Worker with ID '{employee_id}' has been successfully deleted.")

    def update_employee_data(self, login, password, full_name, sex, department, position,
                             hire_date, experience, birth_date, marital_status, phone_number, email):
        """Оновлює дані працівника у базі даних."""
        cursor = self.mydb.cursor()
        query = """
            UPDATE Employee e
            JOIN PersonalInfo p ON e.employee_id = p.employee_id
            JOIN GeneralInfo g ON e.employee_id = g.employee_id
            JOIN Departments d ON g.department_id = d.department_id
            JOIN Positions pos ON g.position_id = pos.position_id
            SET e.full_name = %s, p.birth_date = %s, p.sex = %s, d.department_name = %s,
                pos.position_name = %s, g.hire_date = %s, g.previous_experience = %s,
                p.marital_status = %s, p.phone_number = %s, p.email = %s
            WHERE e.login = %s AND p.password = %s
        """
        cursor.execute(query, (full_name, birth_date, sex, department, position,
                               hire_date, experience, marital_status, phone_number,
                               email, login, password))
        self.mydb.commit()
        cursor.close()

    def get_email_by_id(self, employee_id):
        query = "SELECT email FROM PersonalInfo WHERE employee_id = %s"
        self.cursor.execute(query, (employee_id,))
        result = self.cursor.fetchone()

        return result[0] if result and "@" in result[0] else 0

    def check_and_insert_departments(self, json_path='databases/departments.json'):
        with open(json_path, 'r') as file:
            data = json.load(file)

        self.cursor.execute("SELECT COUNT(*) FROM Departments")
        departments_count = self.cursor.fetchone()[0]

        if departments_count == 0:
            for department_data in data['departments']:
                department = Department(
                    department_name=department_data['name'],
                    department_positions=len(department_data['positions'])
                )

                self.cursor.execute(
                    "INSERT INTO Departments (department_name, department_positions) VALUES (%s, %s)",
                    (department.get_department_name(), department.get_department_positions())
                )
                department_id = self.cursor.lastrowid

                for position in department_data['positions']:
                    self.cursor.execute(
                        "INSERT INTO Positions (department_id, position_name, salary_amount) VALUES (%s, %s, %s)",
                        (department_id, position['name'], position['salary'])
                    )

            self.mydb.commit()
            print("Data inserted successfully!")
        else:
            print("Tables already contain data. No insertion required.")

    def get_departments(self):
        query = "SELECT department_id, department_name FROM Departments"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_positions(self, department_id):
        query = """
            SELECT position_id, position_name
            FROM Positions
            WHERE department_id = %s
        """
        self.cursor.execute(query, (department_id,))
        return self.cursor.fetchall()

    def create_trigger_calculate_experience_generalinfo(self):
        trigger_query = """
            CREATE TRIGGER calculate_experience_generalinfo
            BEFORE INSERT ON GeneralInfo
            FOR EACH ROW
            BEGIN
                SET NEW.total_experience = NEW.previous_experience + YEAR(CURDATE()) - YEAR(NEW.hire_date);
            END
            """
        try:
            self.cursor.execute(trigger_query)
            print("Trigger 'calculate_experience_generalinfo' is successfully created.")
        except mysql.connector.Error as e:
            if "already exists" in str(e):
                print("Trigger already exists.")
            else:
                print(f"Error while creating trigger: {e}")