def compound_interest(k, rate1, rate2, rate3):
    # Calculate the number of months in each interest rate period
    months_rate1 = min(k, 12)
    months_rate2 = min(max(k - 12, 0), 12)
    months_rate3 = max(k - 24, 0)
    
    # Calculate the compound factors for each period
    factor1 = (1 + rate1 / 100) ** months_rate1
    factor2 = (1 + rate2 / 100) ** months_rate2
    factor3 = (1 + rate3 / 100) ** months_rate3
    
    # Total compound factor
    total_factor = factor1 * factor2 * factor3
    
    return total_factor

# Example usage:
k = 36  # Total number of months

rate1 = 5  # Interest rate for months 1-12
rate2 = 6  # Interest rate for months 13-24
rate3 = 7  # Interest rate for months 25 and onward

total_compound_factor = compound_interest(k, rate1, rate2, rate3)
total_interest_percentage = (total_compound_factor - 1) * 100

print(f"Compound interest factor over {k} months: {total_compound_factor:.6f}")
print(f"Total interest earned over {k} months: {total_interest_percentage:.2f}%")
