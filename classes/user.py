import random
import string
import os
import json


class User:
    def __init__(self, login=None, password=None):
        self._ID = self.generate_unique_id()
        self._login = login
        self._password = password

    @staticmethod
    def generate_unique_id():
        used_ids = User.load_used_ids()
        while True:
            new_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            if new_id not in used_ids:
                used_ids.add(new_id)
                User.save_used_ids(used_ids)
                return new_id

    @staticmethod
    def load_used_ids():
        if os.path.exists('used_ids.json'):
            with open('used_ids.json', 'r') as file:
                return set(json.load(file))
        return set()

    @staticmethod
    def save_used_ids(used_ids):
        with open('used_ids.json', 'w') as file:
            json.dump(list(used_ids), file)

    def get_ID(self):
        return self._ID

    def get_login(self):
        return self._login

    def get_password(self):
        return self._password

    def set_ID(self, ID):
        self._ID = ID

    def set_login(self, login):
        self._login = login

    def set_password(self, password):
        self._password = password

