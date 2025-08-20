# ideal_completion.py
import numpy as np
from datetime import datetime, date
from collections import defaultdict
import math

def validate_inputs(inputs, alm_inputs, macro_inputs):
    """Validate all input parameters"""
    # Check financial values
    if inputs.get('start_savings', 0) < 0 or inputs.get('pensionbase', 0) < 0:
        raise ValueError("Financial values cannot be negative")
        
    # Validate age ratio
    age_ratio = convert_to_float(inputs.get('age_ratio', '0'))
    if age_ratio > 1 or age_ratio < 0:
        raise ValueError("Age ratio must be between 0 and 1")
        
    # Validate dates
    if inputs.get('default retirement year') <= inputs.get('birthdate'):
        raise ValueError("Retirement date must be after birth date")
        
    # Validate status
    valid_statuses = ['active', 'retired', 'disabled', 'sleeper']
    if inputs.get('urm status') not in valid_statuses:
        raise ValueError(f"Invalid status. Must be one of {valid_statuses}")
        
    # Validate contribution rates
    for macro in macro_inputs:
        if macro.get('contribution_rate', 0) < 0:
            raise ValueError("Contribution rate cannot be negative")
            
    # Validate data integrity
    if not alm_inputs or len(alm_inputs) < 2:
        raise ValueError("Insufficient ALM data")
    
    years = sorted(item['year'] for item in alm_inputs)
    expected_years = set(range(years[0], years[-1] + 1))
    actual_years = set(years)
    if actual_years != expected_years:
        raise ValueError("Found gaps in ALM data")

def convert_to_float(value):
    try:
        # Attempt to convert the value to float
        return float(value)
    except (ValueError, TypeError):
        # If conversion fails, return a default value or raise an error
        raise ValueError(f"Cannot convert {value} to float")


def increase_years(day, years):
    day = datetime(day.year + years, day.month, day.day)
    return day

def compute_age(now, birthdate):
    return (now - birthdate).days / 365.25

''' 
Create scenario: start by converting xi, ratio, pension_fraction, initial_age, the forecast_year, and the forecast input from the input.
Firstly, the function start_plan_year() is called for the initial year
After that, iterate through all forecast years up until 10th year post-retirement for those not yet retired. For those retired, it's simply 10 years.
The end results represent the outputs on the retirement date and the change factor in the 10th year.
'''
def plan_scenario(first_calc_year, last_forecast_year, scenario_type, inputs, alm_inputs, macro_inputs, retire_age, forecast_year, retire_year, first_year, calc_year):
    """Main scenario planning function with complete validation"""
    # Validate all inputs first
    validate_inputs(inputs, alm_inputs, macro_inputs)
    
    xi = convert_to_float(inputs['age_ratio'])
    ratio = convert_to_float(inputs['ratio'])
    fraction_in_calc_year = calc_year_fraction(inputs['calc_date'])
    initial_age_unrounded = compute_age(inputs['calc_date'], inputs['birthdate'])
    initial_age = math.floor(initial_age_unrounded)
    
    # Determine simulation years
    if inputs['benefit year'] == 0:
        num_years = (retire_year + 10) - first_year + 1
    else:
        num_years = 10  # For retired individuals

    # Generate arrays for time and age
    times = np.arange(first_year, first_year + num_years)
    ages = initial_age + (times - first_year)

    # Forecast years array
    forecast_years = forecast_year + np.arange(num_years)

    # Safe date conversion for retirement calculations
    def safe_date_conversion(year, month, day):
        try:
            return date(year, month, day)
        except ValueError:
            if month == 2 and day == 29:
                return date(year, 2, 28)
            raise

    # Determine if retiring in each year
    is_retiring = np.array([
        inputs["urm status"] != "retired" and find_retiring(
            age, xi, retire_age, inputs['birthdate'],
            safe_date_conversion(time, inputs['calc_date'].month, inputs['calc_date'].day)
        ) for age, time in zip(ages, times)
    ])

    # Retrieve twod and fourd data
    twod_initials = np.array([
        obtain_twod(macro_inputs, fy, scenario_type) for fy in forecast_years
    ])
    twod_nexts = np.array([
        obtain_twod(macro_inputs, fy + 1, scenario_type) for fy in forecast_years
    ])
    fourd_forecasts = [
        obtain_fourds_forecast(age=age, forecast_year=fy, fourd=alm_inputs)
        for age, fy in zip(ages, forecast_years)
    ]

    # Calculate ratios
    taus, pension_fraction_years = zip(*[
        calc_ratios(retire_year, year, inputs) for year in times
    ])
    taus = np.array(taus)
    pension_fraction_years = np.array(pension_fraction_years)

    # Calculate pension base and contribution
    pension_bases, contributions = zip(*[
        calc_pension_base_contribution(inputs, twod_initial)
        for twod_initial in twod_initials
    ])
    pension_bases = np.array(pension_bases)
    contributions = np.array(contributions)

    # Adjust contributions
    contributions = np.where(taus < 1, contributions * taus, 0)

    # Calculate capitals with contributions
    capitals_with_contribution = np.where(
        taus == 0,
        inputs['start_savings'] + contributions,
        0
    )

    # Calculate returns with safety checks
    def safe_return_calculation(*args, **kwargs):
        try:
            return execute_return(*args, **kwargs)
        except Exception:
            return 0.0

    returns_ordinary = np.array([
        safe_return_calculation(
            retire_year_plus1=is_birthday_in_between(fy, inputs['calc_date'],
                                                   inputs['birthdate'],
                                                   inputs['default retirement year']),
            returns=fourd_forecast["fourd_initial_age_init"]['total_return'],
            returns_age_next=fourd_forecast["fourd_initial_age_next"]['total_return'],
            xi=xi,
            pension_fraction_year=pfy,
            is_retiring=ret,
            age=age,
            retire_age=retire_age
        ) for fy, fourd_forecast, pfy, ret, age in zip(forecast_years, fourd_forecasts,
                                                      pension_fraction_years, is_retiring, ages)
    ])

    # Compute capWithContrPostBack with safety
    MAX_VALUE = 1e10
    capWithContrPostBacks = np.minimum(capitals_with_contribution * returns_ordinary, MAX_VALUE)

    # Compute finance factors
    finance_factors = (1 - taus) * np.array([twod['ff'] for twod in twod_initials]) + \
                     taus * np.array([twod['ff'] for twod in twod_nexts])

    # Initialize and compute benefits
    nominal_benefits = np.zeros(num_years)
    nominal_benefits[0] = inputs['benefit year']

    for i in range(1, num_years):
        if is_retiring[i]:
            cwf = cwf_determiner(
                ratio=ratio,
                xi=xi,
                tau=taus[i],
                age=ages[i],
                fourd_initial_age_init=fourd_forecasts[i]["fourd_initial_age_init"],
                fourd_initial_age_next=fourd_forecasts[i]["fourd_initial_age_next"],
                fourd_next_age_next=fourd_forecasts[i]["fourd_next_age_next"],
                fourd_next_age_after=fourd_forecasts[i]["fourd_next_age_after"]
            )
            denominator = cwf * finance_factors[i]
            if abs(denominator) < 1e-10:
                nominal_benefits[i] = 0
            else:
                nominal_benefits[i] = min(capWithContrPostBacks[i] / denominator, MAX_VALUE)
        else:
            payout_change = max(-0.99, min(twod_initials[i]['payout_change'], 100))
            nominal_benefits[i] = nominal_benefits[i-1] * (1 + payout_change)

    # Compute real benefits with safety
    denominators = np.array([
        max(twod['cpi'] * (1 + twod['annual_inflation']) ** pfy, 1e-10)
        if pfy != 0 else 1
        for twod, pfy in zip(twod_initials, pension_fraction_years)
    ])
    
    real_benefits = np.zeros_like(nominal_benefits)
    mask = denominators > 1e-10
    real_benefits[mask] = np.minimum(nominal_benefits[mask] / denominators[mask], MAX_VALUE)

    # Compile outcomes
    outcomes = [
        {
            "year": int(year),
            "forecast_year": int(fy),
            "age": int(age),
            "tau": float(tau),
            "nominal_benefit": float(nb),
            "real_benefit": float(rb),
        }
        for year, fy, age, tau, nb, rb in zip(times, forecast_years, ages,
                                             taus, nominal_benefits, real_benefits)
    ]

    # Handle final calculations with safety
    scenario_outcome = outcomes[-11] if len(outcomes) > 11 else outcomes[0]
    denominator = max(scenario_outcome["real_benefit"], 1e-10)
    mutation_factor = min(outcomes[-1]["real_benefit"] / denominator, MAX_VALUE)

    return {
        "scenario_type": scenario_type,
        "status": inputs["urm status"],
        "years_to_build": int(retire_year - calc_year + 1),
        "scenario_outcome": scenario_outcome,
        "mutation_factor": float(mutation_factor)
    }

def retirement_outcome(data, retire_year):
    
    for record in data:
        if record['year'] == retire_year:
            return record
    return None 

def is_twod_empty(record):
    return record['sr_change'] == 0 and record['payout_change'] == 0 and record['annual_inflation'] == 0 and record['ff'] == 0 and record['cpi'] == 0
        
def find_retiring(age, xi, retire_age, birthdate, forecast_date):
    try:
        # Attempt to construct the date for the forecast year
        adjusted_date = date(forecast_date.year, birthdate.month, birthdate.day)
    except ValueError:
        # Handle the case where the birthdate is February 29 in a non-leap year
        if birthdate.month == 2 and birthdate.day == 29:
            adjusted_date = date(forecast_date.year, 2, 28)
        else:
            raise  # Re-raise the error for other invalid dates

    if adjusted_date <= forecast_date:
        outcome = math.ceil(float(age) + float(xi) - 1.0) == retire_age
    else:
        outcome = math.ceil(float(age) + float(xi)) == retire_age

    return outcome


def is_retiring_start_year(inputs, year):
    
    return inputs['default retirement year'].year == year and float(inputs['benefit year']) == 0.0
    
'''Compute the very first year forecast outcomes as such:
    calculate the ratios (tau and pension_year)
    pension_base and contribution given the inputs. These accumulate to the capital
    Following that, is_retiring indicates whether the person is retiring in this year
    Then, retire_year_plus_1 indicates if the birthday falls between the calculation moment in the forecast and the retirement date.
    After that, given a financial formula, the market returns are retrieved for the scenario and year for this user.
    Then, compute the post-return capital (capWithContrPostBack, capWithPostBack_hon and total_capital). 
    Remember, there are two capitals, one regular and one "-hon" which accumulate the total return. Each has a different rate of return.
    Subsequently, the finance factor is taken from the input and utilized to calculate the nominal benefit and real benefits if the retirement year is reached. 
    All of those are returned. 
    '''
def start_plan_year(forecast_year, ratio, fraction_in_calc_year, xi, retire_year, year, age, inputs, twod_initial, twod_next, fourd_initial_age_init, fourd_initial_age_next, fourd_next_age_next, fourd_next_age_after, retire_age):
    
    (tau, pension_fraction_year) = calc_ratios(retire_year, year, inputs)
    
    (pension_base, contribution) = calc_pension_base_contribution(inputs, twod_initial)
    
    capital_with_contribution = inputs['start_savings'] + contribution if age <= retire_age else 0
    is_retiring = is_retiring_start_year(inputs, year)
    retire_year_plus1 = is_birthday_in_between(forecast_year, inputs['calc_date'], inputs['birthdate'], inputs['default retirement year'])
    (ret_ordinary, ret_honorary) = forecast_returns(retire_year_plus1=retire_year_plus1, xi=xi, pension_fraction_year=pension_fraction_year, is_retiring=is_retiring, age=age, retire_age=retire_age, fourd_initial_age_next=fourd_initial_age_next, fourd_initial_age_init=fourd_initial_age_init)
    (capWithContrPostBack, capWithContrPostBack_hon, total_capital) = compute_savings(capital_with_contribution, ret_ordinary, ret_honorary, retire_age, age, inputs['start_honorary_savings'])
    finance_factor = calc_ff(tau, twod_initial, twod_next) 
        
    nominal_benefit = inputs['benefit year']
    nominal_benefit = determine_nominal_benefit(
        is_retiring=is_retiring,
        nominal_benefit=nominal_benefit,
        retire_year=retire_year, 
        total_capital=total_capital, 
        finance_factor=finance_factor, 
        twod_initial=twod_initial, 
        year=year, 
        ratio=ratio, 
        xi=xi, 
        tau=tau, 
        age=age, 
        fourd_initial_age_init=fourd_initial_age_init,
        fourd_initial_age_next=fourd_initial_age_next,
        fourd_next_age_next=fourd_next_age_next,
        fourd_next_age_after=fourd_next_age_after 
        )        
    
    nominal_benefit_sr = nominal_benefit * (1 + twod_initial["sr_change"]) if year >= retire_year else 0
    survivors_pension = nominal_benefit_sr * ratio
    denominator = twod_initial['cpi'] * (1 + twod_initial['annual_inflation'])**pension_fraction_year
    if denominator == 0:  # Prevent division by zero
        real_benefit = 0
    else:
        real_benefit = nominal_benefit_sr / denominator if year >= retire_year else 0
    
    has_retired = retire_year <= year
    savings_ordinary = 0 if has_retired else capWithContrPostBack - nominal_benefit
    savings_honorary = 0 if has_retired else capWithContrPostBack_hon - survivors_pension / (1 + twod_initial["sr_change"])
    
    return {
        "year": year,
        "forecast_year": forecast_year,
        "age": age,
        "tau": tau,
        "nominal_benefit": nominal_benefit,
        "nominal_benefit_sr": nominal_benefit_sr,
        "real_benefit": real_benefit,
        "capWithContrPostBack": capWithContrPostBack,
        "capWithContrPostBack_hon": capWithContrPostBack_hon,
        "survivors_pension": survivors_pension,
        "total_capital": total_capital,
        "savings_ordinary": savings_ordinary,
        "savings_honorary": savings_honorary
        }

def is_birthday_in_between(forecast_year, calc_date, birthdate, default_retirement_year):
    in_between = False
    year = calc_date.year + forecast_year - 1
    report_date = datetime(year, calc_date.month, calc_date.day)
    birthday_this_year = datetime(year, birthdate.month, birthdate.day)
    #check_formula_1_situations:
    if (report_date <= birthday_this_year < default_retirement_year):
        in_between = True
    
    return in_between 
    
'''Compute the non-initial years forecast outcomes like this:
    ascertain the ratios (tau and pension_year)
    pension_base and contribution based on the inputs. These accumulate to the capital
    Then, is_retiring indicates if the person is retiring in this year
    Next, retire_year_plus_1 signals if the birthday is sandwiched between the calculation moment in the forecast and the retirement date.
    After that, a financial formula provides the market returns for the scenario and year for this person.
    Then, compute the post-back capital (capWithContrPostBack, capWithPostBack_hon and total_capital). 
    Take note: two capitals exist, one regular and one "-hon" which accumulate the total return. Each follows a distinct rate of return.
    Then, acquire the finance factor from the input and utilize it to calculate the nominal and real benefits if the retirement year is achieved. 
    All results are returned. 
    '''
def plan_year(prev_forecast_year, is_retiring, prev_tau, nominal_benefit, savings_ordinary, savings_honorary, forecast_year, ratio, fraction_in_calc_year, xi, retire_year, year, age, inputs, twod_initial, twod_next, fourd_initial_age_init, fourd_initial_age_next, fourd_next_age_next, fourd_next_age_after, retire_age):
    (tau, pension_fraction_year) = calc_ratios(retire_year, year, inputs)
    
    (pension_base, contribution) = calc_pension_base_contribution(inputs, twod_initial)
    if tau > 0 and tau < 1:
        contribution = contribution * tau
    elif tau == 1:
        contribution = 0 
    capital_with_contribution = savings_ordinary + contribution if prev_tau == 0 else 0
    retire_year_plus1 = is_birthday_in_between(forecast_year, inputs['calc_date'], inputs['birthdate'], inputs['default retirement year'])
    (ret_ordinary, ret_honorary) = forecast_returns(retire_year_plus1=retire_year_plus1, xi=xi, pension_fraction_year=pension_fraction_year, is_retiring=is_retiring, age=age, retire_age=retire_age, fourd_initial_age_next=fourd_initial_age_next, fourd_initial_age_init=fourd_initial_age_init)
    (capWithContrPostBack, capWithContrPostBack_hon, total_capital) = compute_savings(capital_with_contribution, ret_ordinary, ret_honorary, retire_age, age, savings_honorary)
    finance_factor = calc_ff(tau, twod_initial, twod_next)    
    
    nominal_benefit = determine_nominal_benefit(
        is_retiring=is_retiring,
        nominal_benefit=nominal_benefit,
        retire_year=retire_year, 
        total_capital=total_capital, 
        finance_factor=finance_factor, 
        twod_initial=twod_initial, 
        year=year, 
        ratio=ratio, 
        xi=xi, 
        tau=tau, 
        age=age, 
        fourd_initial_age_init=fourd_initial_age_init,
        fourd_initial_age_next=fourd_initial_age_next,
        fourd_next_age_next=fourd_next_age_next,
        fourd_next_age_after=fourd_next_age_after 
        )
        
    nominal_benefit_sr = nominal_benefit * (1 + twod_initial["sr_change"]) if nominal_benefit > 0 else 0
    survivors_pension = nominal_benefit_sr * ratio
    denominator = (twod_initial['cpi'] * (1 + twod_initial['annual_inflation'])**pension_fraction_year) 
    if denominator == 0.0:
        denominator = 1.0
    real_benefit = nominal_benefit_sr / denominator if nominal_benefit > 0 else 0
    
    savings_ordinary = capWithContrPostBack
    savings_honorary = capWithContrPostBack_hon
   
    return {
        "year": year,
        "forecast_year": forecast_year,
        "age": age,
        "tau": tau,
        "nominal_benefit": nominal_benefit,
        "nominal_benefit_sr": nominal_benefit_sr,
        "real_benefit": real_benefit,
        "capWithContrPostBack": capWithContrPostBack,
        "capWithContrPostBack_hon": capWithContrPostBack_hon,
        "total_capital": total_capital,
        "survivors_pension": survivors_pension,
        "savings_ordinary": savings_ordinary,
        "savings_honorary": savings_honorary
        }

def compute_savings(capWithContr, ret_ordinary, ret_honorary, retire_age, age, savings_honorary):
    capWithContrPostBack = capWithContr * ret_ordinary 
    capWithContrPostBack_hon = savings_honorary * ret_honorary 
    total_capital = capWithContrPostBack + capWithContrPostBack_hon 
    return (capWithContrPostBack, capWithContrPostBack_hon, total_capital)

def calc_ff(tau, twod_initial, twod_next):
    finance_factor = (1-tau) * twod_initial['ff'] + tau * twod_next['ff'] 
    return finance_factor

def calc_pension_base_contribution(inputs, twod_initial):
    pension_base = inputs['pensionbase'] * twod_initial['cpi']
    contribution = pension_base * twod_initial["contribution_rate"] 
    
    return (pension_base, contribution)

def calc_ratios(retire_year, year, inputs):
    tau = determine_tau_for_year(retire_year, year, inputs)
    if inputs['urm status'] == 'disabled' or inputs['urm status'] == 'active' or inputs['urm status'] == 'sleeper':
        pension_fraction_year = inputs['year fraction retirement year']
    else:
        pension_fraction_year = 0
    return (tau, pension_fraction_year)


def obtain_twod(twod, forecast_year, scenario_type):
    for record in twod:
        if record["year"] == forecast_year:
            return record
    # If no matching entry is found
    return {
        'year': forecast_year,
        'sr_change': 0,
        'scenario': scenario_type,
        'payout_change': 0,
        'annual_inflation': 0,
        'ff': 0,
        'cpi': 0,
        'contribution_rate': 0
    }

   
def cwf_determiner(xi, tau, ratio, age, fourd_initial_age_init, fourd_initial_age_next, fourd_next_age_next, fourd_next_age_after):
    
    cwf_op_current0 = (1-xi) * fourd_initial_age_init['op_cwf'] + xi * fourd_initial_age_next['op_cwf']
    cwf_pp_current0 = (1-xi) * fourd_initial_age_init['pp_cwf'] + xi * fourd_initial_age_next['pp_cwf']
    
    cwf_op_current1 = (1-xi) * fourd_next_age_next['op_cwf'] + xi * fourd_next_age_after['op_cwf']
    cwf_pp_current1 = (1-xi) * fourd_next_age_next['pp_cwf'] + xi * fourd_next_age_after['pp_cwf']
   
    cwf_op = (1-tau) * cwf_op_current0 + tau * cwf_op_current1
    cwf_pp = (1-tau) * cwf_pp_current0 + tau * cwf_pp_current1
    
    return cwf_op + ratio * cwf_pp

def determine_nominal_benefit(is_retiring, nominal_benefit, retire_year, total_capital, finance_factor, twod_initial, year, ratio, xi, tau, age, fourd_initial_age_init, fourd_initial_age_next, fourd_next_age_next, fourd_next_age_after):
    if is_retiring:
        cwf = cwf_determiner(
            ratio=ratio, 
            xi=xi,
            tau=tau,
            age=age,
            fourd_initial_age_init=fourd_initial_age_init,
            fourd_initial_age_next=fourd_initial_age_next,
            fourd_next_age_next=fourd_next_age_next,
            fourd_next_age_after=fourd_next_age_after   
            )
        nominal_benefit = total_capital / (cwf * finance_factor)
    else:
        nominal_benefit = nominal_benefit * (1 + twod_initial['payout_change'])
    return nominal_benefit


def determine_tau_for_year(retire_year, year, inputs):
    if inputs["birthdate"].year + 67 == year:
        tau = convert_to_float(inputs['year fraction retirement year'])
    elif retire_year > year:
        tau = 0
    else: 
        tau = 1
    return tau

def refresh_retiring(age, retire_age, outcomes, index, revised_forecast_year, inputs, xi):
    if inputs["urm status"] == "active" or inputs["urm status"] == "sleeper":
        is_retiring = inputs["urm status"] == "retired"
    if find_retiring(age, xi, retire_age, inputs['birthdate'], date(int(inputs['calc_date'].year + revised_forecast_year - 1), inputs['calc_date'].month, inputs['calc_date'].day)):
        is_retiring = True
    return is_retiring    

def refresh_age(initial_age_unrounded, revised_forecast_year, index, outcomes):
    if outcomes[index] is not None and outcomes[index]['forecast_year'] == revised_forecast_year: 
        age = math.ceil(initial_age_unrounded - 1 + revised_forecast_year)
    else:
        age = outcomes[index]['age'] + 1
    return age

def refresh_year(outcomes, index, revised_forecast_year):
    if outcomes[index]['forecast_year'] == revised_forecast_year:
        year = outcomes[index]['year']
    else:
        year = outcomes[index]['year'] + 1
    return year       
           
def forecast_returns(retire_year_plus1, xi, pension_fraction_year, is_retiring, age, retire_age, fourd_initial_age_next, fourd_initial_age_init):
    ret_ordinary = execute_return(
        retire_year_plus1=retire_year_plus1, 
        is_retiring=is_retiring, age=age, retire_age=retire_age,
        returns_age_next=fourd_initial_age_next['total_return'], returns=fourd_initial_age_init['total_return'], xi=xi, 
        pension_fraction_year=pension_fraction_year)
    ret_honorary = execute_return(
        retire_year_plus1=retire_year_plus1, 
        is_retiring=is_retiring, age=age, retire_age=retire_age,
        returns_age_next=fourd_initial_age_next['total_return_honorary'], returns=fourd_initial_age_init['total_return_honorary'], xi=xi, 
        pension_fraction_year=pension_fraction_year)

    return (ret_ordinary, ret_honorary)

def execute_return(retire_year_plus1, returns, returns_age_next, xi, pension_fraction_year, is_retiring, age, retire_age):
    outcome = 1
    a = 1 + returns
    b = 1 + returns_age_next
    condition1 = is_retiring
    if (condition1): 
        if (retire_year_plus1):   
            first = raise_to_power(a, 1-xi)
            second = raise_to_power(b, pension_fraction_year-(1-xi))
            outcome = first * second
        else:
            outcome = raise_to_power(a, pension_fraction_year)
    else:
        first = raise_to_power(a, 1-xi)
        second = raise_to_power(b, xi)
        outcome = first * second
    return outcome

def raise_to_power(num, exp):
    if num == 0.0:
        return 0.0
    if exp == 0.0:
        return 1.0
    return num**exp
    

def calc_year_fraction(calc_date):
    days_difference = date(calc_date.year, calc_date.month, calc_date.day) - date(calc_date.year,1,1)
    year_fraction = days_difference.days / 365.25
    return year_fraction
def obtain_fourds_forecast(age, forecast_year, fourd):
    return {
        "fourd_initial_age_init": fetch_fourd(fourd, age, forecast_year),
        "fourd_initial_age_next": fetch_fourd(fourd, age+1, forecast_year),
        "fourd_next_age_next": fetch_fourd(fourd, age+1, forecast_year+1),
        "fourd_next_age_after": fetch_fourd(fourd, age+2, forecast_year + 1)
        }
def prepare_fourd_data(fourd_for_scenario):
    cohorts_per_year = defaultdict(dict)
    for entry in fourd_for_scenario:
        year = entry["year"]
        cohort = entry["cohort"]
        cohorts_per_year[year][cohort] = entry
    return cohorts_per_year

def fetch_fourd(fourd_for_scenario, age, forecast_year):
    cohorts_per_year = prepare_fourd_data(fourd_for_scenario)
    return cohorts_per_year.get(forecast_year, {}).get(age, {
        "year": forecast_year,
        "scenario": fourd_for_scenario[0]['scenario'],
        "cohort": age,
        "op_cwf": 0.0,
        "pp_cwf": 0.0,
        "total_return": 0.0,
        "total_return_honorary": 0.0
    })
