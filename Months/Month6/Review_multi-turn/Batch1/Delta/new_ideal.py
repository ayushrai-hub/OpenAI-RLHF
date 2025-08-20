# ideal_completion.py

import threading
import time
import random
from array import array

def simulate_race_condition(num_threads=5, iterations=50000, initial_balance=1000.0):
    account_balance = initial_balance
    
    # Pre-calculate random numbers to avoid generating them in the loop
    random_array = array('f', [random.random() for _ in range(10)])
    
    def complex_operation(value):
        # Use pre-calculated random numbers and avoid list comprehension
        total = 0
        for r in random_array:
            total += value * r
        return total
    
    def withdraw():
        nonlocal account_balance
        for _ in range(iterations):
            temp_balance = account_balance
            result = complex_operation(temp_balance)
            new_balance = temp_balance - 0.01 - (result * 0.000001)
            account_balance = new_balance
    
    thread_list = []
    for _ in range(num_threads):  # Fixed syntax error in original
        thread = threading.Thread(target=withdraw)
        thread_list.append(thread)
        thread.start()
    
    for thread in thread_list:
        thread.join()
        
    expected_balance = initial_balance - (num_threads * iterations * 0.01)
    return account_balance, expected_balance

if __name__ == "__main__":  # Fixed syntax error in original
    final_balance, expected = simulate_race_condition()
    print(f"Final account balance: {final_balance:.2f}")
    print(f"Expected balance: {expected:.2f}")