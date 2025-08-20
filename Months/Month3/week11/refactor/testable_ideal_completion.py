
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from typing import List, Dict, Any, Tuple

def parse_date(date_string: str) -> date:
    """Parse a date string in 'YYYY-MM-DD' format to a date object."""
    return datetime.strptime(date_string, '%Y-%m-%d').date()

def get_month_start(reference_date: date, months_ago: int) -> date:
    """Retrieve the initial date of the month from a given number of months ago, relative to a reference date."""
    beginning_of_month = reference_date.replace(day=1)
    earlier_date = beginning_of_month - relativedelta(months=months_ago)
    return earlier_date

def calculate_liability_balances(liabilities: List[Dict[str, Any]], start_date: date, end_date: date) -> Dict[str, float]:
    """Determine the balances for liabilities that existed within a specified date range."""
    compiled_balances = {}

    for liability in liabilities:
        # Interpret dates
        start_of_liability = parse_date(liability['start_date'])
        end_of_liability = parse_date(liability['end_date'])

        # Verify if the liability was present within the date range
        if end_of_liability >= start_date and start_of_liability <= end_date:
            category = liability['type']

            if category not in compiled_balances:
                compiled_balances[category] = 0
            compiled_balances[category] += liability['balance']

    return compiled_balances

def process_liabilities(liabilities: List[Dict[str, Any]], time_windows: List[int]) -> List[Tuple[int, date, Dict[str, float], float]]:
    """Process liabilities for different time windows and return balances over each window."""
    current_date = datetime.now().date()
    result = []

    for period in time_windows:
        starting_date = get_month_start(current_date, period)
        balances_acquired = calculate_liability_balances(liabilities, starting_date, current_date)
        overall_balance = sum(balances_acquired.values())
        result.append((period, starting_date, balances_acquired, overall_balance))

    return result