#ideal_completion.py

def main():
    change = int(input())
    if change <= 0:
        print("No change")
    else:
        # Calculate the number of each coin type
        quarters = change // 25
        change %= 25
        dimes = change // 10
        change %= 10
        nickels = change // 5
        change %= 5
        pennies = change

        # Check and print for each coin type
        if quarters > 0:
            print(f"{quarters} Quarter{'s' if quarters > 1 else ''}")
        if dimes > 0:
            print(f"{dimes} Dime{'s' if dimes > 1 else ''}")
        if nickels > 0:
            print(f"{nickels} Nickel{'s' if nickels > 1 else ''}")
        if pennies > 0:
            print(f"{pennies} {'Pennies' if pennies > 1 else 'Penny'}")

if __name__ == '__main__':
    main()