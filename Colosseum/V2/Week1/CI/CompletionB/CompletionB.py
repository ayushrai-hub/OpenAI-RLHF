def compound_interest(k, rate1, rate2, rate3):
    amount = 1.0  # Starting with a principal amount of 1
    total_months = k

    # Interest rate for months 1-12
    if total_months > 0:
        months = min(total_months, 12)
        monthly_rate = rate1 / 100 / 12  # Convert annual rate to monthly decimal
        amount *= (1 + monthly_rate) ** months
        total_months -= months

    # Interest rate for months 13-24
    if total_months > 0:
        months = min(total_months, 12)
        monthly_rate = rate2 / 100 / 12
        amount *= (1 + monthly_rate) ** months
        total_months -= months

    # Interest rate for months above 24
    if total_months > 0:
        months = total_months
        monthly_rate = rate3 / 100 / 12
        amount *= (1 + monthly_rate) ** months

    return amount

# Example usage:
k = 36  # Total number of months
rate1 = 5  # Interest rate for months 1-12 (annual percentage rate)
rate2 = 6  # Interest rate for months 13-24
rate3 = 7  # Interest rate for months above 24

compound_interest_rate = compound_interest(k, rate1, rate2, rate3)
print("Compound amount after {} months is {:.4f}".format(k, compound_interest_rate))
print("Total interest earned: {:.2f}%".format((compound_interest_rate - 1) * 100))
