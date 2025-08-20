import threading
import time

account_balance = 1000.0
expected_deductions = 0.0

def withdraw(thread_id):
    global account_balance, expected_deductions
    for _ in range(50000):
        # Simulate a more complex operation
        temp = account_balance
        time.sleep(0.0000001)  # Introduce a small delay
        temp -= 0.01
        account_balance = temp
        
        # Track expected deductions
        expected_deductions += 0.01

def benchmark():
    start_time = time.time()
    
    num_threads = 5
    threads = []
    
    for i in range(num_threads):
        thread = threading.Thread(target=withdraw, args=(i,))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    end_time = time.time()
    
    print(f"Initial balance: 1000.0")
    print(f"Expected final balance: {1000.0 - expected_deductions:.2f}")
    print(f"Actual final balance: {account_balance:.2f}")
    print(f"Discrepancy: {abs(account_balance - (1000.0 - expected_deductions)):.2f}")
    print(f"Execution time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    benchmark()