from classes.personal_info import *

class Employee():
    def __init__(self, employee_id: str, full_name: str = None):
        self._employee_ID = employee_id
        self._full_name = full_name

    def get_employee_ID(self) -> str:
        return self._employee_ID

    def get_full_name(self) -> str:
        return self._full_name

    def set_employee_ID(self, employee_ID: str):
        self._employee_ID = employee_ID

    def set_full_name(self, full_name: str):
        self._full_name = full_name
