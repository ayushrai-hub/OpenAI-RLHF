import threading
import time

def simulate_race_condition(num_threads: int = 5, iterations: int = 50000, initial_balance: float = 1000.0) -> tuple[float, float]:
    account_balance = [initial_balance]  # Using a list to make it mutable inside threads

    def withdraw():
        for _ in range(iterations):
            temp_balance = account_balance[0]  # Read balance
            # Simulating a delayed operation
            time.sleep(0.0000001)
            # Compute new balance
            temp_balance -= 0.01
            account_balance[0] = temp_balance  # Write back the new balance

    thread_list = []

    for _ in range(num_threads):
        thread = threading.Thread(target=withdraw)
        thread_list.append(thread)
        thread.start()

    for thread in thread_list:
        thread.join()

    expected_balance = initial_balance - (num_threads * iterations * 0.01)
    return account_balance[0], expected_balance
