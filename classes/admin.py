class Admin:
    def __init__(self, login="admin", email="staff-base@ukr.net", password_key="admin:password"):
        self._login = login
        self._email = email
        self._password_key = password_key

        def get_login(self):
            return self._login

        def get_email(self):
            return self._email

        def get_password_key(self):
            return self._password_key
