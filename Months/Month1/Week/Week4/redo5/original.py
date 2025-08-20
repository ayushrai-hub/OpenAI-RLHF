# Type your code here.
def main():
    change = int(input())

    dol_value = change // 100
    quarter_value = (change % 100) // 25
    dime_value = (change % 25) // 10
    nickel_value = (change % 10) // 5
    penny_value = change % 5

    if change <= 0:
        print("No change")
    else:
        if dol_value > 1:
            print(f'{dol_value} Dollars')
        elif dol_value == 1:
            print(f'{dol_value} Dollar')
        
        if quarter_value > 1:
            print(f'{quarter_value} Quarters')
        elif quarter_value == 1:
            print(f'{quarter_value} Quarter')
        
        if dime_value > 1:
            print(f'{dime_value} Dimes')
        elif dime_value == 1:
            print(f'{dime_value} Dime')
        
        if nickel_value > 1:
            print(f'{nickel_value} Nickels')
        elif nickel_value == 1:
            print(f'{nickel_value} Nickel')
        
        if penny_value > 1:
            print(f'{penny_value} Pennies')
        elif penny_value == 1:
            print(f'{penny_value} Penny')

# Run the main function
if __name__ == "__main__":
    main()