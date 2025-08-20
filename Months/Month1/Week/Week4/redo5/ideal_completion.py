#ideal_completion.py

def main():
    # Get input from user
    change = int(input())

    # Handle no change case
    if change <= 0:
        print("No change")
        return

    # Calculate coin values
    dollars = change // 100
    change %= 100
    
    quarters = change // 25
    change %= 25
    
    dimes = change // 10
    change %= 10
    
    nickels = change // 5
    pennies = change % 5

    # Output change using conditional logic
    if dollars > 0:
        print(f"{dollars} Dollar{'s' if dollars > 1 else ''}")
    
    if quarters > 0:
        print(f"{quarters} Quarter{'s' if quarters > 1 else ''}")
    
    if dimes > 0:
        print(f"{dimes} Dime{'s' if dimes > 1 else ''}")
    
    if nickels > 0:
        print(f"{nickels} Nickel{'s' if nickels > 1 else ''}")
    
    if pennies > 0:
        print(f"{pennies} Penn{'ies' if pennies > 1 else 'y'}")

# Run the main function
if __name__ == "__main__":
    main()