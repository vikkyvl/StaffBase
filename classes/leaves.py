from datetime import date
from classes.employee import Employee

class Leaves:
    def __init__(self, employee_id: str, leave_type: str, start_date: date, end_date: date):
        self._employee_id = employee_id
        self._leave_type = leave_type if leave_type in ('Sick', 'Vacation', 'Time Off') else None
        self._start_date = start_date
        self._end_date = end_date if end_date >= start_date else start_date
        self._duration = self._calculate_duration()

    def get_employee_id(self) -> str:
        return self._employee_id

    def get_leave_type(self) -> str:
        return self._leave_type

    def get_start_date(self) -> date:
        return self._start_date

    def get_end_date(self) -> date:
        return self._end_date

    def get_duration(self) -> int:
        return self._duration

    def set_leave_type(self, leave_type: str):
        if leave_type in ('Sick', 'Vacation', 'Time Off'):
            self._leave_type = leave_type

    def set_start_date(self, start_date: date):
        if start_date <= self._end_date:
            self._start_date = start_date
            self._duration = self._calculate_duration()

    def set_end_date(self, end_date: date):
        if end_date >= self._start_date:
            self._end_date = end_date
            self._duration = self._calculate_duration()

    def _calculate_duration(self) -> int:
        return (self._end_date - self._start_date).days + 1
