from datetime import date
from classes.employee import Employee

class PersonalInfo:
    def __init__(self, birth_date: date, sex: str, number_of_children: int, phone_number: int, marital_status: str, email: str):
        self._birth_date = birth_date
        self._sex = sex
        self._number_of_children = number_of_children
        self._phone_number = phone_number
        self._marital_status = marital_status
        self._email = email

    def get_birth_date(self) -> date:
        return self._birth_date

    def get_sex(self) -> str:
        return self._sex

    def get_number_of_children(self) -> int:
        return self._number_of_children

    def get_phone_number(self) -> int:
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

    def set_phone_number(self, phone_number: int):
        self._phone_number = phone_number

    def set_marital_status(self, marital_status: str):
        self._marital_status = marital_status

    def set_email(self, email: str):
        self._email = email

