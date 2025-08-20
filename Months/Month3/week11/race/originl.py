import threading
import time

account_balance = 1000.0

def withdraw():
    global account_balance
    for _ in range(50000):
        # Introduce a small delay.
        temp_balance = account_balance  # Read balance
        # Simulating a delayed operation
        time.sleep(0.0000001)
        # Compute new balance
        temp_balance -= 0.01
        account_balance = temp_balance  # Write back the new balance

def main():
    num_threads = 5
    thread_list = []

    for _ in range(num_threads):
        thread = threading.Thread(target=withdraw)
        thread_list.append(thread)
        thread.start()

    for thread in thread_list:
        thread.join()

    print(f"Final account balance: {account_balance}")

if __name__ == "__main__":
    main()
