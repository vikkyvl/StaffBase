class Employee:
    def __init__(self, employee_id, full_name=None):
        self._employee_id = employee_id
        self._full_name = full_name

    def set_full_name(self, full_name):
        self._full_name = full_name
