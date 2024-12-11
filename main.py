from design.auth_pages_main import run_application
from imports import *

def run():
    # app = Application()
    # app.mainloop()
    # redis_connection = Redis()
    # mysql_connection = MySQL()
    #
    # print(redis_connection)
    # print(mysql_connection)
    # redis_connection.set_new_admin_password("1235")
    # print(redis_connection.get_admin_password())
    # print(redis_connection.update_employee_password("vlada_petryk", "1234f"))
    # print(redis_connection.get_id_by_login("vika_thebest"))
    # print(redis_connection.delete_employee("vika_thebest"))
    run_application()


if __name__ == "__main__":
    print("HElLO")
    run()