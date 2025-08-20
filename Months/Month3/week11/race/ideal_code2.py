import threading
import time
import random

def simulate_race_condition(num_threads=5, iterations=50000, initial_balance=1000.0):
    account_balance = initial_balance

    def complex_operation(value):
        return sum([value * random.random() for _ in range(1000)])

    def withdraw():
        nonlocal account_balance
        for _ in range(iterations):
            temp_balance = account_balance
            result = complex_operation(temp_balance)
            time.sleep(random.uniform(0, 0.0001))
            new_balance = temp_balance - 0.01 - (result * 0.000001)
            account_balance = new_balance

    thread_list = []
    for _ in range(num_threads):
        thread = threading.Thread(target=withdraw)
        thread_list.append(thread)
        thread.start()

    for thread in thread_list:
        thread.join()

    expected_balance = initial_balance - (num_threads * iterations * 0.01)
    return account_balance, expected_balance

if __name__ == "__main__":
    final_balance, expected = simulate_race_condition()
    print(f"Final account balance: {final_balance:.2f}")
    print(f"Expected balance: {expected:.2f}")