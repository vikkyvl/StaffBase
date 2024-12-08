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

    def set_ID(self, ID):
        self._ID = ID

    def set_login(self, login):
        self._login = login

    def set_password(self, password):
        self._password = password
