def print_number_pattern(n):
    for i in range(n):
        num = i + 1
        d = n - 1
        for j in range(2):
            print(num, end="")
            num += d
            d -= 1
        print()

# Example usage
if __name__ == "__main__":
    n = int(input("Enter the number of rows: "))
    print_number_pattern(n)