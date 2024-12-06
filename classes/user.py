class User:
    def __init__(self, ID=None, login=None, password=None):
        self._ID = ID
        self._login = login
        self._password = password

    def get_ID(self):
        return self._ID

    def get_login(self):
        return self._login

    def get_password(self):
        return self._password
