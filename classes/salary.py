from employee import Employee

class Salary:
    def __init__(self, employee: Employee, month: str, salary: float):
        self._employee = employee
        self._month = month
        self._salary = salary

    def get_employee_ID(self) -> str:
        return self._employee.get_employee_ID()

    def get_month(self) -> str:
        return self._month

    def get_salary(self) -> float:
        return self._salary

    def set_employee_ID(self, employee_ID: str):
        self._employee.set_employee_ID(employee_ID)

    def set_month(self, month: str):
        self._month = month

    def set_salary(self, salary: float):
        self._salary = salary