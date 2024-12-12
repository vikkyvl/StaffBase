from datetime import date
from classes.employee import Employee

class Leaves:
    def __init__(self, employee: Employee, leave_type: str, start_date: date, end_date: date, duration: int):
        self._employee = employee
        self._leave_type = leave_type
        self._start_date = start_date
        self._end_date = end_date
        self._duration = duration

    def get_employee_ID(self) -> str:
        return self._employee.get_employee_ID()

    def get_leave_type(self) -> str:
        return self._leave_type

    def get_start_date(self) -> date:
        return self._start_date

    def get_end_date(self) -> date:
        return self._end_date

    def get_duration(self) -> int:
        return self._duration

    def set_leave_type(self, leave_type: str):
        self._leave_type = leave_type

    def set_start_date(self, start_date: date):
        self._start_date = start_date

    def set_end_date(self, end_date: date):
        self._end_date = end_date

    def set_duration(self, duration: int):
        self._duration = duration
