def compound_interest(k, rate1, rate2, rate3):
    total_multiplier = 1.0  # Start with the base amount
    
    if k <= 12:
        # Only within the first 12 months
        total_multiplier *= (1 + rate1/100) ** k
    elif k <= 24:
        # Split between first and second rate period
        total_multiplier *= (1 + rate1/100) ** 12  # First 12 months at rate1
        total_multiplier *= (1 + rate2/100) ** (k - 12)  # Remaining months at rate2
    else:
        # Split across all three periods
        total_multiplier *= (1 + rate1/100) ** 12  # First 12 months at rate1
        total_multiplier *= (1 + rate2/100) ** 12  # Months 13-24 at rate2
        total_multiplier *= (1 + rate3/100) ** (k - 24)  # Remaining months beyond 24 at rate3
    
    return total_multiplier

# Example usage:
k = 36  # Total months
rate1 = 5  # Interest rate for months 1-12
rate2 = 6  # Interest rate for months 13-24
rate3 = 7  # Interest rate for months over 24

compound_interest_multiplier = compound_interest(k, rate1, rate2, rate3)
print("Total compound interest multiplier for {} months: {:.4f}".format(k, compound_interest_multiplier))
