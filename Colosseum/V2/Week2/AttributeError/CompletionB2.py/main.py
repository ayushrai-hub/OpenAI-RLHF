from database_lib import database_library  # Import your class correctly

class MainClass:
    def __init__(self):
        self.obj_database_lib = database_library()

    def wakeup_protocol(self):
        try:
            if not self.check_trade_or_not():
                print("wakeup started")

                users = self.obj_database_lib.user_details()

                if users is not None:
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        broker_obj = [broker_library(user) for user in users]
                        results = list(executor.map(broker_library.update_stock_user_mapping, broker_obj))

                        print(results)

                    obj_log_lib.all_logs('wakeup_protocol', 'wakeup_protocol Done', self.wakeup_protocol.__name__, self.__class__.__name__)
                    print("wakeup_protocol: Done")
                else:
                    print("No user found")
                    obj_log_lib.all_logs('wakeup_protocol', 'No user found', self.wakeup_protocol.__name__, self.__class__.__name__)

        except Exception as e:
            print('wakeup_protocol:', e)
            traceback.print_exc()
            obj_log_lib.all_logs("wakeup protocol Error", traceback.format_exc(), self.wakeup_protocol.__name__, self.__class__.__name__)
            obj_log_lib.error_logs("wakeup protocol Error", traceback.format_exc(), self.wakeup_protocol.__name__, self.__class__.__name__)
