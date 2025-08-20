import time
import random

def bubble_organize(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            # Compare adjacent elements and swap if they're in the wrong order
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

def selection_organize(arr):
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i+1, n):
            # Find the minimum element in the unsorted portion
            if arr[j] < arr[min_idx]:
                min_idx = j
        # Swap the found minimum element with the first element
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr

def insertion_organize(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        # Move elements greater than key to one position ahead
        while j >= 0 and key < arr[j]:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr

def merge_organize(arr):
    if len(arr) > 1:
        mid = len(arr) // 2
        L = arr[:mid]
        R = arr[mid:]

        # Recursively organize the two halves
        merge_organize(L)
        merge_organize(R)

        i = j = k = 0

        # Merge the two sorted halves
        while i < len(L) and j < len(R):
            if L[i] < R[j]:
                arr[k] = L[i]
                i += 1
            else:
                arr[k] = R[j]
                j += 1
            k += 1

        # Check for any remaining elements
        while i < len(L):
            arr[k] = L[i]
            i += 1
            k += 1

        while j < len(R):
            arr[k] = R[j]
            j += 1
            k += 1
    return arr

def quick_organize(arr):
    if len(arr) <= 1:
        return arr
    else:
        pivot = arr[len(arr) // 2]
        left = [x for x in arr if x < pivot]
        middle = [x for x in arr if x == pivot]
        right = [x for x in arr if x > pivot]
        return quick_organize(left) + middle + quick_organize(right)

def heap_organize(arr):
    def heapify(arr, n, i):
        largest = i
        l = 2 * i + 1
        r = 2 * i + 2

        if l < n and arr[largest] < arr[l]:
            largest = l
        if r < n and arr[largest] < arr[r]:
            largest = r

        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            heapify(arr, n, largest)

    n = len(arr)

    # Build a maxheap
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)

    # Extract elements from the heap one by one
    for i in range(n - 1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]
        heapify(arr, i, 0)

    return arr

def radix_organize(arr):
    if not arr:
        return arr  # Return empty list if input is empty

    # Find maximum absolute value in the array
    max_abs = max(abs(num) for num in arr)

    # Function to get the digit at a specific place value
    def get_digit(num, exp):
        return abs(num) // exp % 10

    # Counting sort function
    def counting_sort(arr, exp):
        n = len(arr)
        output = [0] * n
        count = [0] * 10

        for i in range(n):
            index = get_digit(arr[i], exp)
            count[index] += 1

        for i in range(1, 10):
            count[i] += count[i - 1]

        i = n - 1
        while i >= 0:
            index = get_digit(arr[i], exp)
            output[count[index] - 1] = arr[i]
            count[index] -= 1
            i -= 1

        for i in range(n):
            arr[i] = output[i]

    # Radix sort
    exp = 1
    while max_abs // exp > 0:
        counting_sort(arr, exp)
        exp *= 10

    # Handle negative numbers
    neg = [num for num in arr if num < 0]
    pos = [num for num in arr if num >= 0]
    arr[:] = sorted(neg, reverse=True) + pos

    return arr

def counting_organize(arr):
    if not arr:
        return arr  # Return empty list if input is empty

    max_val = max(arr)
    min_val = min(arr)
    range_val = max_val - min_val + 1

    count = [0] * range_val

    for num in arr:
        count[num - min_val] += 1

    i = 0
    for j in range(range_val):
        while count[j] > 0:
            arr[i] = j + min_val
            i += 1
            count[j] -= 1

    return arr
def shell_organize(arr):
    n = len(arr)
    gap = n // 2

    while gap > 0:
        for i in range(gap, n):
            temp = arr[i]
            j = i
            while j >= gap and arr[j - gap] > temp:
                arr[j] = arr[j - gap]
                j -= gap
            arr[j] = temp
        gap //= 2

    return arr

def main():
    # Generate a random list of integers
    arr = [random.randint(1, 1000) for _ in range(1000)]
    
    # List of organizing functions
    organize_functions = [
        bubble_organize,
        selection_organize,
        insertion_organize,
        merge_organize,
        quick_organize,
        heap_organize,
        radix_organize,
        counting_organize,
        shell_organize
    ]

    # Test each organizing function
    for func in organize_functions:
        # Create a copy of the original array
        test_arr = arr.copy()
        
        # Measure the time taken to organize
        start_time = time.time()
        organized_arr = func(test_arr)
        end_time = time.time()
        
        # Check if the array is correctly organized
        is_organized = all(organized_arr[i] <= organized_arr[i+1] for i in range(len(organized_arr)-1))
        
        # Print results
        print(f"{func.__name__}:")
        print(f"  Time taken: {end_time - start_time:.6f} seconds")
        print(f"  Correctly organized: {is_organized}")
        print()

if __name__ == "__main__":
    main()