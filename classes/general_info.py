from datetime import date
from classes.employee import Employee

class GeneralInfo():
    def __init__(self, department_id: int, position_id: int, hire_date: date, experience: int):
        self._department_ID = department_id
        self._position_ID = position_id
        self._hire_date = hire_date
        self._experience = experience

    def get_department_ID(self) -> int:
        return self._department_ID

    def get_position_ID(self) -> int:
        return self._position_ID

    def get_hire_date(self) -> date:
        return self._hire_date

    def get_experience(self) -> int:
        return self._experience

    def set_department_ID(self, department_ID: int):
        self._department_ID = department_ID

    def set_position_ID(self, position_ID: int):
        self._position_ID = position_ID

    def set_hire_date(self, hire_date: date):
        self._hire_date = hire_date

    def set_experience(self, experience: int):
        self._experience = experience