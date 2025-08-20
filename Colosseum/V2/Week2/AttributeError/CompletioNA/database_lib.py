# database_lib.py

class database_library:
    def user_details(self):
        try:
            with get_connection() as conn, conn.cursor() as mycursor:
                mycursor.execute("SELECT * FROM user_broker_details WHERE connection_status=True")
                rows = mycursor.fetchall()
                user_data = [dict(zip([key[0] for key in mycursor.description], row)) for row in rows]
                return user_data
        except Exception as e:
            print("user_details Error :", e)
            obj_log_lib.all_logs('user_details', 'Error ', inspect.stack()[0][3], self.__class__.__name__)
            obj_log_lib.error_logs('user_details Error', traceback.format_exc(), inspect.stack()[0][3], self.__class__.__name__)
