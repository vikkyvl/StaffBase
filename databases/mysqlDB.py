import mysql.connector

class MySQL:
    def __init__(self, host="35.238.85.91", port=3306, user="root", password="v-7@", use_pure=True):
        self.mydb = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            use_pure=use_pure
        )