def compute_compound_interest(k, rate1, rate2, rate3):
    total_amount = 1  # Assuming principal amount is 1 for calculating the interest rate effect
    
    # Compute interest for the first 12 months
    if k <= 12:
        total_amount *= (1 + rate1 / 100) ** k
    else:
        total_amount *= (1 + rate1 / 100) ** 12
        
        # Compute interest for the next 12 months (months 13 to 24)
        if k <= 24:
            months_in_second_period = k - 12
            total_amount *= (1 + rate2 / 100) ** months_in_second_period
        else:
            total_amount *= (1 + rate2 / 100) ** 12
            
            # Compute interest for the remaining months beyond 24
            months_in_third_period = k - 24
            total_amount *= (1 + rate3 / 100) ** months_in_third_period
    
    # The result is the compounded total amount, so we subtract 1 to get only the interest part
    return total_amount - 1

# Example usage:
k = 36  # Duration in months
rate1 = 5  # Annual interest rate for months 1-12
rate2 = 6  # Annual interest rate for months 13-24
rate3 = 7  # Annual interest rate for months beyond 24

compound_interest_result = compute_compound_interest(k, rate1, rate2, rate3)
print("Compound interest for {} months is {:.2f}%".format(k, compound_interest_result * 100))
