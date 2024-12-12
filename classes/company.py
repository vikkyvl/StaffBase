from classes.department import Department

class Company:
    def __init__(self, company_name: str, num_of_departments: int):
        self._company_name = company_name
        self._num_of_departments = num_of_departments
        self._departments = []

    def get_company_name(self) -> str:
        return self._company_name

    def get_num_of_departments(self) -> int:
        return self._num_of_departments

    def set_company_name(self, company_name: str):
        self._company_name = company_name

    def set_num_of_departments(self, num_of_departments: int):
        self._num_of_departments = num_of_departments

    def add_department(self, department: Department):
        self._departments.append(department)

