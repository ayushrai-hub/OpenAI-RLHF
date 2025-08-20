def compound_interest(k, rate1, rate2, rate3):
    if k <= 12:
        return (1 + rate1/100) ** k
    elif k <= 24:
        # First 12 months at rate1, remaining at rate2
        return (1 + rate1/100) ** 12 * (1 + rate2/100) ** (k - 12)
    else:
        # First 12 at rate1, next 12 at rate2, remaining at rate3
        return (1 + rate1/100) ** 12 * (1 + rate2/100) ** 12 * (1 + rate3/100) ** (k - 24)

# Example usage:
k = 36
rate1 = 5  # Interest rate for first 12 months
rate2 = 6  # Interest rate for months 13-24
rate3 = 7  # Interest rate for months 25+

compound_interest_result = compound_interest(k, rate1, rate2, rate3)
print("Compound interest rate for {} months is {:.4f}".format(k, compound_interest_result))
