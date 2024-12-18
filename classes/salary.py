from classes.employee import Employee

class Salary:
    def __init__(self, employee_id: str, month: str, salary: float):
        self._employee_id = employee_id
        self._month = month
        self._salary = salary

    def get_employee_id(self) -> str:
        return self._employee_id

    def get_month(self) -> str:
        return self._month

    def get_salary(self) -> float:
        return self._salary

    def set_month(self, month: str):
        self._month = month

    def set_salary(self, salary: float):
        self._salary = salary
