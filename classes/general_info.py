from datetime import date

class GeneralInfo:
    def __init__(
        self,
        employee_id: str,
        department_id: int,
        position_id: int,
        hire_date: date,
        experience: int
    ):
        self._employee_id = employee_id
        self._department_id = department_id
        self._position_id = position_id
        self._hire_date = hire_date
        self._experience = experience

    def get_employee_id(self) -> str:
        return self._employee_id

    def get_department_id(self) -> int:
        return self._department_id

    def get_position_id(self) -> int:
        return self._position_id

    def get_hire_date(self) -> date:
        return self._hire_date

    def get_experience(self) -> int:
        return self._experience

    def set_department_id(self, department_id: int):
        self._department_id = department_id

    def set_position_id(self, position_id: int):
        self._position_id = position_id

    def set_hire_date(self, hire_date: date):
        self._hire_date = hire_date

    def set_experience(self, experience: int):
        self._experience = experience
