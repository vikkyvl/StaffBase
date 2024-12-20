import calendar
import json
import mysql.connector
from classes.leaves import Leaves
from classes.department import Department
from classes.employee import Employee
from classes.general_info import GeneralInfo
from classes.personal_info import PersonalInfo
from classes.salary import Salary


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
            self.create_update_duration_trigger()

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
                    department_positions INT DEFAULT 0,
                    average_salary DECIMAL(10, 2) DEFAULT 0.00
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
                    marital_status ENUM('', 'Single', 'Married'),
                    email VARCHAR(255),
                    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id) ON DELETE CASCADE
                )
            """,
            "Salary": """
                CREATE TABLE IF NOT EXISTS Salary (
                    employee_id VARCHAR(36),
                    salary_month VARCHAR(7) NOT NULL,
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
            query,(personal_info.get_employee_id(), personal_info.get_birth_date(), personal_info.get_sex(), personal_info.get_number_of_children(), personal_info.get_phone_number(), personal_info.get_marital_status(), personal_info.get_email())
        )
        self.mydb.commit()
        cursor.close()

    def add_employee_salary(self, salary: Salary):
        try:
            cursor = self.mydb.cursor()
            query = """INSERT INTO Salary (employee_id, salary_month, salary_amount)
                       VALUES (%s, %s, %s)"""

            cursor.execute(
                query, (salary.get_employee_id(), salary.get_month(), salary.get_salary())
            )
            self.mydb.commit()
            cursor.close()
        except Exception as e:
            print(f"Error adding employee salary: {e}")
            raise

    def add_leave_request(self, employee_id, leave_type, start_date, end_date):
        cursor = self.mydb.cursor()
        query = """INSERT INTO Leaves (employee_id, leave_type, start_date, end_date)
                   VALUES (%s, %s, %s, %s)"""
        try:
            cursor.execute(query, (employee_id, leave_type, start_date, end_date))
            self.mydb.commit()
        except Exception as e:
            print(f"Error adding leave request: {e}")
            self.mydb.rollback()
        finally:
            cursor.close()

    def delete_worker_by_id(self, employee_id):
        delete_query = "DELETE FROM Employee WHERE employee_id = %s"
        self.cursor.execute(delete_query, (employee_id,))
        self.mydb.commit()
        print(f"Worker with ID '{employee_id}' has been successfully deleted.")

    def delete_leave_request(self, employee_id, leave_type, start_date, end_date):
        delete_query = """
            DELETE FROM Leaves
            WHERE employee_id = %s AND leave_type = %s AND start_date = %s AND end_date = %s
        """
        try:
            cursor = self.mydb.cursor()
            cursor.execute(delete_query, (employee_id, leave_type, start_date, end_date))
            self.mydb.commit()
            print(f"Leave request for employee '{employee_id}' from {start_date} to {end_date} has been deleted.")
        except Exception as e:
            print(f"Error deleting leave request: {e}")
            self.mydb.rollback()
        finally:
            cursor.close()

    def update_employee(self, data):
        try:
            query_employee = """
                UPDATE Employee
                SET full_name = %s
                WHERE employee_id = %s
            """
            self.cursor.execute(query_employee, (data["full_name"], data["employee_id"]))

            query_general_info = """
                UPDATE GeneralInfo
                SET department_id = %s,
                    position_id = %s,
                    hire_date = %s,
                    previous_experience = %s
                WHERE employee_id = %s
            """
            self.cursor.execute(query_general_info, (data["department_id"], data["position_id"], data["hire_date"], data["experience"], data["employee_id"]))

            query_personal_info = """
                UPDATE PersonalInfo
                SET birth_date = %s,
                    sex = %s,
                    phone_number = %s,
                    marital_status = %s,
                    email = %s
                WHERE employee_id = %s
            """
            self.cursor.execute(query_personal_info, (data["birth_date"], data["sex"], data["phone_number"], data["marital_status"], data["email"], data["employee_id"]))

            self.mydb.commit()
            return True
        except mysql.connector.Error as e:
            print(f"Error while updating employee data: {e}")
            self.mydb.rollback()
            return False

    def update_personal_info(self, data):
        try:
            query = """
                UPDATE PersonalInfo
                SET number_of_children = %s, marital_status = %s, phone_number = %s, email = %s
                WHERE employee_id = %s
            """
            self.cursor.execute(query, (data["number_of_children"], data["marital_status"], data["phone_number"], data["email"], data["employee_id"]))

            self.mydb.commit()
            return True
        except mysql.connector.Error as e:
            print(f"Error updating personal info: {e}")
            self.mydb.rollback()
            return False

    def update_leave_request(self, employee_id, leave_type, start_date, end_date):
        cursor = self.mydb.cursor()
        query = """UPDATE Leaves 
                   SET leave_type = %s, start_date = %s, end_date = %s 
                   WHERE employee_id = %s"""
        try:
            cursor.execute(query, (leave_type, start_date, end_date, employee_id))
            self.mydb.commit()
        except Exception as e:
            print(f"Error updating leave request: {e}")
            self.mydb.rollback()
        finally:
            cursor.close()

    def update_user_email(self, worker_id, email):
        query = "UPDATE PersonalInfo SET email = %s WHERE employee_id = %s"
        try:
            self.cursor.execute(query, (email, worker_id))
            self.mydb.commit()
        except Exception as e:
            print(f"Error updating email: {e}")
            self.mydb.rollback()

    def get_employee_id_by_name(self, full_name):
        cursor = self.mydb.cursor()
        query = "SELECT employee_id FROM Employee WHERE full_name = %s"
        try:
            cursor.execute(query, (full_name,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Error fetching employee ID: {e}")
            return None
        finally:
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

    def get_all_workers(self):
        query = "SELECT employee_id, full_name FROM Employee"
        try:
            cursor = self.mydb.cursor()
            cursor.execute(query)
            workers = cursor.fetchall()
            return workers
        except Exception as e:
            print(f"Error fetching workers: {e}")
            return []
        finally:
            cursor.close()

    def get_email_by_id(self, employee_id):
        query = "SELECT email FROM PersonalInfo WHERE employee_id = %s"
        self.cursor.execute(query, (employee_id,))
        result = self.cursor.fetchone()

        if not result or result[0] is None:
            return None
        return result[0] if "@" in result[0] else 0

    def get_all_leave_requests(self):
        cursor = self.mydb.cursor()
        query = """SELECT e.full_name, l.leave_type, l.start_date, l.end_date, l.duration
                   FROM Leaves l
                   JOIN Employee e ON l.employee_id = e.employee_id"""
        try:
            cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error fetching leave requests: {e}")
            return []
        finally:
            cursor.close()

    def get_all_salaries_with_names(self):
        query = """
            SELECT e.full_name, s.salary_month, s.salary_amount
            FROM Salary s
            JOIN Employee e ON s.employee_id = e.employee_id
            ORDER BY s.salary_month DESC
        """
        try:
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            return results
        except Exception as e:
            print(f"Error fetching salaries: {e}")
            return []

    def get_employee_salary_by_month(self, employee_id, salary_month):
        query = """
            SELECT salary_amount
            FROM Salary
            WHERE employee_id = %s AND salary_month = %s
        """
        try:
            self.cursor.execute(query, (employee_id, salary_month))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error checking salary for {employee_id} in {salary_month}: {e}")
            return None

    def get_employee_leaves(self, employee_id, salary_month):
        query = """
                    SELECT leave_type, duration
                    FROM Leaves
                    WHERE employee_id = %s AND start_date BETWEEN %s AND %s
                """
        year, month = map(int, salary_month.split("-"))
        last_day = calendar.monthrange(year, month)[1]
        start_date = f"{salary_month}-01"
        end_date = f"{salary_month}-{last_day:02d}"
        try:
            self.cursor.execute(query, (employee_id, start_date, end_date))
            result = self.cursor.fetchall()
            return [{'leave_type': row[0], 'duration': row[1]} for row in result]
        except Exception as e:
            print(f"Error fetching employee leaves: {e}")
            return []


    def get_info_for_request(self, employee_id):
        query = """
            SELECT e.full_name, c.company_name, p.email
            FROM Employee e
            JOIN PersonalInfo p ON e.employee_id = p.employee_id
            JOIN Company c
            WHERE e.employee_id = %s
        """
        try:
            self.cursor.execute(query, (employee_id,))
            result = self.cursor.fetchone()
            if result:
                return {
                    "full_name": result[0],
                    "company_name": result[1],
                    "email": result[2]
                }
            else:
                return None
        except Exception as e:
            return None

    def get_employee_full_info(self, employee_id):
        query = """
            SELECT 
                e.full_name,
                d.department_name,
                p.position_name,
                g.hire_date,
                g.total_experience,
                pi.birth_date,
                pi.sex,
                pi.number_of_children,
                pi.phone_number,
                pi.marital_status,
                pi.email
            FROM Employee e
            JOIN GeneralInfo g ON e.employee_id = g.employee_id
            JOIN Departments d ON g.department_id = d.department_id
            JOIN Positions p ON g.position_id = p.position_id
            JOIN PersonalInfo pi ON e.employee_id = pi.employee_id
            WHERE e.employee_id = %s
        """
        try:
            self.cursor.execute(query, (employee_id,))
            result = self.cursor.fetchone()

            if result:
                return {
                    "full_name": result[0],
                    "department_name": result[1],
                    "position_name": result[2],
                    "hire_date": result[3],
                    "total_experience": result[4],
                    "birth_date": result[5],
                    "sex": result[6],
                    "number_of_children": result[7],
                    "phone_number": result[8],
                    "marital_status": result[9],
                    "email": result[10]
                }
            else:
                print("No data found for the given employee ID.")
                return None
        except Exception as e:
            print(f"Error fetching employee information: {e}")
            return None

    def get_employee_info_for_calculation_salary(self, employee_id):
        query = """
            SELECT E.full_name, P.salary_amount, GI.total_experience
            FROM Employee E
            JOIN GeneralInfo GI ON E.employee_id = GI.employee_id
            JOIN Positions P ON GI.position_id = P.position_id
            WHERE E.employee_id = %s
        """
        try:
            self.cursor.execute(query, (employee_id,))
            result = self.cursor.fetchone()
            if result:
                return {
                    'employee_id': employee_id,
                    'full_name': result[0],
                    'salary_amount': result[1],
                    'total_experience': result[2]
                }
            return None
        except Exception as e:
            print(f"Error fetching employee info for salary calculation: {e}")
            return None

    def get_salary_history(self, employee_id):
        query = """
            SELECT 
                salary_month, 
                salary_amount 
            FROM 
                Salary
            WHERE 
                employee_id = %s
            ORDER BY 
                salary_month DESC
        """
        try:
            cursor = self.mydb.cursor(dictionary=True)
            cursor.execute(query, (employee_id,))
            results = cursor.fetchall()
            return results
        except Exception as e:
            print(f"Error fetching salary history: {e}")
            return []
        finally:
            cursor.close()

    def get_leaves_history(self, employee_id):
        query = """
            SELECT 
                leave_type,
                start_date,
                end_date,
                duration
            FROM 
                Leaves
            WHERE 
                employee_id = %s
        """
        try:
            cursor = self.mydb.cursor(dictionary=True)
            cursor.execute(query, (employee_id,))
            results = cursor.fetchall()
            return results
        except Exception as e:
            print(f"Error fetching leaves: {e}")
            return []
        finally:
            cursor.close()

    def get_retirement_age_employees(self):
        cursor = self.mydb.cursor(dictionary=True)
        query = """
            SELECT 
                e.employee_id,
                e.full_name,
                TIMESTAMPDIFF(YEAR, p.birth_date, CURDATE()) AS age,
                g.total_experience AS experience
            FROM 
                Employee e
            JOIN 
                PersonalInfo p ON e.employee_id = p.employee_id
            JOIN 
                GeneralInfo g ON e.employee_id = g.employee_id
            WHERE 
                TIMESTAMPDIFF(YEAR, p.birth_date, CURDATE()) >= 60;
        """
        try:
            cursor.execute(query)
            results = cursor.fetchall()
            return results
        except Exception as e:
            print(f"Error fetching retirement age employees: {e}")
            return []
        finally:
            cursor.close()

    def get_employees_below_average_salary(self):
        cursor = self.mydb.cursor(dictionary=True)
        query = """
            SELECT 
                d.department_name,
                d.average_salary, 
                e.full_name,
                p.salary_amount
            FROM 
                Employee e
            JOIN 
                GeneralInfo g ON e.employee_id = g.employee_id
            JOIN 
                Departments d ON g.department_id = d.department_id
            JOIN 
                Positions p ON g.position_id = p.position_id
            WHERE 
                p.salary_amount < d.average_salary;
        """
        try:
            cursor.execute(query)
            results = cursor.fetchall()
            return results
        except Exception as e:
            print(f"Error fetching employees with earnings below department average: {e}")
            return []
        finally:
            cursor.close()

    def get_average_age_by_department_and_company(self):
        cursor = self.mydb.cursor(dictionary=True)

        try:
            department_query = """
                SELECT 
                    d.department_name,
                    ROUND(AVG(TIMESTAMPDIFF(YEAR, p.birth_date, CURDATE()))) AS average_age
                FROM 
                    Employee e
                JOIN 
                    PersonalInfo p ON e.employee_id = p.employee_id
                JOIN 
                    GeneralInfo g ON e.employee_id = g.employee_id
                JOIN 
                    Departments d ON g.department_id = d.department_id
                GROUP BY 
                    d.department_name
            """
            cursor.execute(department_query)
            department_results = cursor.fetchall()

            company_query = """
                SELECT 
                    ROUND(AVG(TIMESTAMPDIFF(YEAR, p.birth_date, CURDATE()))) AS average_age_company
                FROM 
                    PersonalInfo p
            """
            cursor.execute(company_query)
            company_result = cursor.fetchone()

            return department_results, company_result

        except Exception as e:
            print(f"Error fetching average age: {e}")
            return None, None

        finally:
            cursor.close()

    def get_sick_leave_duration_by_department(self):
        cursor = self.mydb.cursor(dictionary=True)
        try:
            total_query = """
                SELECT 
                    d.department_name,
                    SUM(l.duration) AS total_leave_duration
                FROM 
                    Leaves l
                JOIN 
                    GeneralInfo g ON l.employee_id = g.employee_id
                JOIN 
                    Departments d ON g.department_id = d.department_id
                WHERE 
                    l.leave_type = 'Sick'
                GROUP BY 
                    d.department_name
            """
            cursor.execute(total_query)
            total_results = cursor.fetchall()

            monthly_query = """
                SELECT 
                    d.department_name,
                    MONTH(l.start_date) AS leave_month,
                    SUM(l.duration) AS total_leave_duration
                FROM 
                    Leaves l
                JOIN 
                    GeneralInfo g ON l.employee_id = g.employee_id
                JOIN 
                    Departments d ON g.department_id = d.department_id
                WHERE 
                    l.leave_type = 'Sick'
                GROUP BY 
                    d.department_name, leave_month
            """
            cursor.execute(monthly_query)
            monthly_results = cursor.fetchall()

            return total_results, monthly_results

        except Exception as e:
            print(f"Error fetching sick leave duration: {e}")
            return None, None
        finally:
            cursor.close()

    def get_average_experience_by_department(self):
        query = """
            SELECT 
                d.department_name,
                ROUND(AVG(g.total_experience), 2) AS average_experience
            FROM 
                GeneralInfo g
            JOIN 
                Departments d ON g.department_id = d.department_id
            GROUP BY 
                d.department_name
        """
        try:
            cursor = self.mydb.cursor(dictionary=True)
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Exception as e:
            print(f"Error retrieving average work experience by department: {e}")
            return []

    def get_average_earnings_by_gender_and_department(self):
        department_query = """
            SELECT 
                d.department_name,
                p.sex,
                ROUND(AVG(s.salary_amount), 2) AS average_salary
            FROM 
                Employee e
            JOIN 
                PersonalInfo p ON e.employee_id = p.employee_id
            JOIN 
                GeneralInfo g ON e.employee_id = g.employee_id
            JOIN 
                Departments d ON g.department_id = d.department_id
            JOIN 
                Salary s ON e.employee_id = s.employee_id
            GROUP BY 
                d.department_name, p.sex
        """

        company_query = """
            SELECT 
                p.sex,
                ROUND(AVG(s.salary_amount), 2) AS average_salary_company
            FROM 
                Employee e
            JOIN 
                PersonalInfo p ON e.employee_id = p.employee_id
            JOIN 
                Salary s ON e.employee_id = s.employee_id
            GROUP BY 
                p.sex
        """

        try:
            cursor = self.mydb.cursor(dictionary=True)

            cursor.execute(department_query)
            department_results = cursor.fetchall()

            cursor.execute(company_query)
            company_results = cursor.fetchall()

            cursor.close()
            return department_results, company_results

        except Exception as e:
            print(f"Error retrieving average earnings by gender: {e}")
            return [], []

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

    def check_user_email(self, worker_id):
        query = "SELECT email FROM PersonalInfo WHERE employee_id = %s"
        try:
            self.cursor.execute(query, (worker_id,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Error checking user email: {e}")
            return None

    def check_and_insert_departments(self, json_path='databases/departments.json'):
        with open(json_path, 'r') as file:
            data = json.load(file)

        self.cursor.execute("SELECT COUNT(*) FROM Company")
        company_count = self.cursor.fetchone()[0]

        if company_count == 0:
            num_of_departments = len(data['departments'])
            self.cursor.execute(
                "INSERT INTO Company (company_name, num_of_departments) VALUES (%s, %s)",
                ("IT Academy", num_of_departments)
            )
            print("Company IT Academy inserted successfully!")

            for department_data in data['departments']:
                department_name = department_data['name']
                department_positions = len(department_data['positions'])

                total_salary = sum(position['salary'] for position in department_data['positions'])
                average_salary = total_salary / department_positions if department_positions > 0 else 0

                self.cursor.execute(
                    "INSERT INTO Departments (department_name, department_positions, average_salary) VALUES (%s, %s, %s)",
                    (department_name, department_positions, average_salary)
                )
                department_id = self.cursor.lastrowid

                for position in department_data['positions']:
                    self.cursor.execute(
                        "INSERT INTO Positions (department_id, position_name, salary_amount) VALUES (%s, %s, %s)",
                        (department_id, position['name'], position['salary'])
                    )

            self.mydb.commit()
            print("Departments, positions, and average salaries inserted successfully!")
        else:
            print("Company data already exists. No insertion required.")

    def create_trigger_calculate_experience_generalinfo(self):
        trigger_insert_query = """
            CREATE TRIGGER calculate_experience_generalinfo_before_insert
            BEFORE INSERT ON GeneralInfo
            FOR EACH ROW
            BEGIN
                SET NEW.total_experience = NEW.previous_experience + YEAR(CURDATE()) - YEAR(NEW.hire_date);
            END;
        """

        trigger_update_query = """
            CREATE TRIGGER calculate_experience_generalinfo_before_update
            BEFORE UPDATE ON GeneralInfo
            FOR EACH ROW
            BEGIN
                SET NEW.total_experience = NEW.previous_experience + YEAR(CURDATE()) - YEAR(NEW.hire_date);
            END;
        """

        try:
            self.cursor.execute(trigger_insert_query)
            print("Trigger 'calculate_experience_generalinfo_before_insert' is successfully created.")
        except mysql.connector.Error as e:
            if "already exists" in str(e):
                print("Trigger 'calculate_experience_generalinfo_before_insert' already exists.")
            else:
                print(f"Error while creating INSERT trigger: {e}")

        try:
            self.cursor.execute(trigger_update_query)
            print("Trigger 'calculate_experience_generalinfo_before_update' is successfully created.")
        except mysql.connector.Error as e:
            if "already exists" in str(e):
                print("Trigger 'calculate_experience_generalinfo_before_update' already exists.")
            else:
                print(f"Error while creating UPDATE trigger: {e}")

    def create_update_duration_trigger(self):
        cursor = self.mydb.cursor()
        trigger_query = """
            CREATE TRIGGER IF NOT EXISTS update_duration_on_update
            BEFORE UPDATE ON Leaves
            FOR EACH ROW
            BEGIN
                SET NEW.duration = DATEDIFF(NEW.end_date, NEW.start_date) + 1;
            END;
        """
        try:
            cursor.execute(trigger_query)
            self.mydb.commit()
            print("Trigger 'update_duration_on_update' created successfully.")
        except Exception as e:
            print(f"Error creating trigger: {e}")
            self.mydb.rollback()
        finally:
            cursor.close()