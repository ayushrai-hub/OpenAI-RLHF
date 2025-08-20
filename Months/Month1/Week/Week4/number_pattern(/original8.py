def print_number_pattern(n):


    for i in range(n):
        num = 1  # or num = 1 + i if you want it to depend on the loop index
        d = n - 1
        
        for j in range(0, 2):  # Changed loop variable to j and fixed the range
            print(num, end="")
            num += d
            d -= 1
        
        print()  # Moves to the next line after inner loop
