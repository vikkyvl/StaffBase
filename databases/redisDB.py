import redis
from classes.admin import *
from classes.user import *

class Redis(Admin, User):
    def __init__(self, host='redis-13066.c124.us-central1-1.gce.redns.redis-cloud.com', port=13066, username="default", password="5i0VNFZWaNcR9oPNzHdrO2ZSPKHUDdXe"):
        super().__init__()
        self.r = redis.Redis(
            host=host,
            port=port,
            decode_responses=True,
            username=username,
            password=password
        )

    def get_admin_password(self):
        return self.r.get(self.get_password_key())

    def set_new_admin_password(self, new_password):
        self.r.set(self.get_password_key(), new_password)

    def is_exist_user(self, login):
        return 1 if self.r.hexists(f"user:{login}", "password") else 0

    def add_employee(self, user_info):
        self.r.hset(f"user:{user_info.get_login()}", mapping={"id": user_info.get_ID(), "password": user_info.get_password()})

    def update_employee_password(self, login, new_password):
        if self.is_exist_user(login):
            self.r.hset(f"user:{login}", "password", new_password)
            return 1
        return 0

    def get_id_by_login(self, login):
        if self.is_exist_user(login):
            return self.r.hget(f"user:{login}", "id")
        return 0

    def delete_employee(self, login):
        if self.is_exist_user(login):
            self.r.delete(f"user:{login}")
            return 1
        return 0






