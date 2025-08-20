def print_number_pattern(n):
    for i in range(n):
        num = 1 + 1
        d = n - 1
        
        for i in range(0, 1 + 1):
            print(num, end="")
            num += d
            d -= 1
        
        print()
