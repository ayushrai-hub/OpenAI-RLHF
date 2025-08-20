change = int(input())

if change <= 0:
    print("No change")
else:
    denominations = [
        (100, "Dollar", "Dollars"),
        (25, "Quarter", "Quarters"),
        (10, "Dime", "Dimes"),
        (5, "Nickel", "Nickels"),
        (1, "Penny", "Pennies")
    ]
    
    output = []
    
    for value, singular, plural in denominations:
        count = change // value
        if count > 0:
            if count == 1:
                output.append(f"1 {singular}")
            else:
                output.append(f"{count} {plural}")
        change %= value
    
    for line in output:
        print(line)