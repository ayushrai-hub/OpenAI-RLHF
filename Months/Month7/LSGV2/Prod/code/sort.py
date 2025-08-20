import random
import time
import statistics

# Generate a dataset of 10,000 random integers
def generate_data(n=10000, seed=None):
    if seed is not None:
        random.seed(seed)
    return [random.randint(0, 100000) for _ in range(n)]

# Implement Bubble Sort
def bubble_sort(arr):
    a = arr.copy()
    n = len(a)
    for i in range(n):
        for j in range(0, n - i - 1):
            if a[j] > a[j+1]:
                a[j], a[j+1] = a[j+1], a[j]
    return a

# Implement Merge Sort
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged

# Implement Quick Sort
def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    mid = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + mid + quick_sort(right)

# Measure execution time
def measure(func, arr):
    start = time.perf_counter()
    func(arr)
    end = time.perf_counter()
    return end - start

# Compare sorting algorithms
def compare_algorithms(n=10000, runs=5):
    results = {name: [] for name in ['QuickSort', 'MergeSort', 'BubbleSort']}
    
    data = generate_data(n)
    first_run_times = {name: measure(func, data) for name, func in [('QuickSort', quick_sort), ('MergeSort', merge_sort), ('BubbleSort', bubble_sort)]}
    
    for _ in range(runs - 1):
        data = generate_data(n)
        for name, func in [('QuickSort', quick_sort), ('MergeSort', merge_sort), ('BubbleSort', bubble_sort)]:
            results[name].append(measure(func, data))
    
    avg_times = {name: statistics.mean(times) for name, times in results.items()}
    return first_run_times, avg_times

# Single run on fresh dataset
data = generate_data()
times_single = {name: measure(func, data) for name, func in [('QuickSort', quick_sort), ('MergeSort', merge_sort), ('BubbleSort', bubble_sort)]}

# Run with fixed seed
data_fixed = generate_data(seed=0)
times_fixed = {name: measure(func, data_fixed) for name, func in [('QuickSort', quick_sort), ('MergeSort', merge_sort), ('BubbleSort', bubble_sort)]}

# Run comparisons
first_run_times, avg_times = compare_algorithms()

# Print results
print("First Run Times:", first_run_times)
print("\n Fixed Seed Run:", times_fixed)
print("\nAverage Times Over Multiple Runs:", avg_times)
print("\n Single Run Times:", times_single)
