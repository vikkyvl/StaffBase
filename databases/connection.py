from databases.redisDB import Redis
from databases.mysqlDB import MySQL

class Connection:
    def __init__(self):
        self.redis_connection = Redis()
        self.mysql_connection = MySQL()

    def __del__(self):
        if hasattr(self, 'redis_connection') and self.redis_connection:
            try:
                self.redis_connection.r.close()
            except Exception as e:
                print(f"Error closing Redis connection: {e}")

        if hasattr(self, 'mysql_connection') and self.mysql_connection:
            try:
                if self.mysql_connection.cursor:
                    self.mysql_connection.cursor.close()
                if self.mysql_connection.mydb:
                    self.mysql_connection.mydb.close()
            except Exception as e:
                print(f"Error closing MySQL connection: {e}")
