def compound_interest(k, rate1, rate2, rate3):
    result = 1
    
    if k > 24:
        result *= (1 + rate1/100) ** 12  # First 12 months
        result *= (1 + rate2/100) ** 12  # Next 12 months
        result *= (1 + rate3/100) ** (k - 24)  # Remaining months
    elif k > 12:
        result *= (1 + rate1/100) ** 12  # First 12 months
        result *= (1 + rate2/100) ** (k - 12)  # Remaining months
    else:
        result *= (1 + rate1/100) ** k  # All months at rate1
    
    return result

# Example usage:
k = 36
rate1 = 5  # Interest rate for 1-12 months
rate2 = 6  # Interest rate for 12-24 months
rate3 = 7  # Interest rate for over 24 months

compound_interest_result = compound_interest(k, rate1, rate2, rate3)
print("Compound interest factor for {} months is {:.4f}".format(k, compound_interest_result))
print("Total interest earned: {:.2f}%".format((compound_interest_result - 1) * 100))
