class Department:
    def __init__(self, department_ID: int, department_name: str, department_positions: str):
        self._department_ID = department_ID
        self._department_name = department_name
        self._department_positions = department_positions

    def get_department_ID(self) -> int:
        return self._department_ID

    def get_department_name(self) -> str:
        return self._department_name

    def get_department_positions(self) -> str:
        return self._department_positions

    def set_department_ID(self, department_ID: int):
        self._department_ID = department_ID

    def set_department_name(self, department_name: str):
        self._department_name = department_name

    def set_department_positions(self, department_positions: str):
        self._department_positions = department_positions
