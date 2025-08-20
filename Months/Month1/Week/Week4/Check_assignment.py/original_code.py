def print_number_pattern(n):
    for i in range(n):
        num = 1
        d = n - 1
        
        for j in range(2):
            print(num, end="")
            num += d
            d -= 1
        
        print()  # Moves to the next line after inner loop

# This part is for testing the function directly
if __name__ == "__main__":
    n = int(input("Enter a number: "))
    print_number_pattern(n)