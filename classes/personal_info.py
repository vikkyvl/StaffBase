from datetime import date

class PersonalInfo:
    def __init__(
        self,
        employee_id: str,
        birth_date: date,
        sex: str,
        number_of_children: int = 0,
        phone_number: str = None,
        marital_status: str = None,
        email: str = None
    ):
        self._employee_id = employee_id
        self._birth_date = birth_date
        self._sex = sex
        self._number_of_children = number_of_children
        self._phone_number = phone_number
        self._marital_status = marital_status
        self._email = email

    def get_employee_id(self) -> str:
        return self._employee_id

    def get_birth_date(self) -> date:
        return self._birth_date

    def get_sex(self) -> str:
        return self._sex

    def get_number_of_children(self) -> int:
        return self._number_of_children

    def get_phone_number(self) -> str:
        return self._phone_number

    def get_marital_status(self) -> str:
        return self._marital_status

    def get_email(self) -> str:
        return self._email

    def set_birth_date(self, birth_date: date):
        self._birth_date = birth_date

    def set_sex(self, sex: str):
        self._sex = sex

    def set_number_of_children(self, number_of_children: int):
        self._number_of_children = number_of_children

    def set_phone_number(self, phone_number: str):
        self._phone_number = phone_number

    def set_marital_status(self, marital_status: str):
        self._marital_status = marital_status

    def set_email(self, email: str):
        self._email = email
