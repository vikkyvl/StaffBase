class Position:
    def __init__(self, position_id: int, department_id: int, position_name: str, salary_amount: float):
        self._position_id = position_id
        self._department_id = department_id
        self._position_name = position_name
        self._salary_amount = salary_amount

    def get_position_id(self) -> int:
        return self._position_id

    def get_department_id(self) -> int:
        return self._department_id

    def get_position_name(self) -> str:
        return self._position_name

    def get_salary_amount(self) -> float:
        return self._salary_amount

    def set_position_id(self, position_id: int):
        self._position_id = position_id

    def set_department_id(self, department_id: int):
        self._department_id = department_id

    def set_position_name(self, position_name: str):
        self._position_name = position_name

    def set_salary_amount(self, salary_amount: float):
        if salary_amount >= 0:
            self._salary_amount = salary_amount