#ideal_completion.py

from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import logging
from typing import List, Dict, Any, Tuple
from decimal import Decimal, ROUND_HALF_UP

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_month_start(reference_date: date, months_ago: int) -> date:
    return (reference_date.replace(day=1) - relativedelta(months=months_ago))

def parse_date(date_string: str) -> date:
    try:
        return datetime.strptime(date_string, '%Y-%m-%d').date()
    except ValueError as e:
        logging.error(f"Invalid date format: {date_string}")
        raise ValueError(f"Invalid date format. Expected 'YYYY-MM-DD', got '{date_string}'") from e

def calculate_liability_balances(liabilities: List[Dict[str, Any]], start_date: date, end_date: date) -> Dict[str, float]:
    balances = {}
    
    for liability in liabilities:
        try:
            liability_start = parse_date(liability['start_date'])
            liability_end = parse_date(liability['end_date'])
            balance = Decimal(str(liability['balance']))

            if liability_start <= end_date and liability_end >= start_date:
                overlap_start = max(liability_start, start_date)
                overlap_end = min(liability_end, end_date)
                overlap_days = (overlap_end - overlap_start).days + 1
                liability_days = (liability_end - liability_start).days + 1
                
                prorated_balance = (balance * Decimal(overlap_days) / Decimal(liability_days)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                
                liability_type = liability['type']
                balances[liability_type] = balances.get(liability_type, Decimal('0')) + prorated_balance
        except KeyError as e:
            logging.error(f"Missing key in liability data: {e}")
            raise ValueError(f"Invalid liability data: missing key {e}")
        except ValueError as e:
            logging.error(f"Error processing liability: {e}")
            raise

    return {k: float(v) for k, v in balances.items()}

def process_liabilities(liabilities: List[Dict[str, Any]], time_windows: List[int]) -> List[Tuple[int, date, Dict[str, float], float]]:
    if not liabilities:
        logging.info("No liabilities provided.")
        return []

    try:
        reference_date = max(parse_date(liability['end_date']) for liability in liabilities if 'end_date' in liability)
        if not isinstance(reference_date, date):
            raise ValueError("No valid end dates found in liabilities")
    except ValueError as e:
        logging.error(f"Error determining reference date: {e}")
        raise

    results = []
    for months in time_windows:
        start_date = get_month_start(reference_date, months - 1)
        balances = calculate_liability_balances(liabilities, start_date, reference_date)
        total_balance = sum(balances.values())
        results.append((months, start_date, balances, total_balance))

    return results

def main():
    liabilities = [
        {"type": "Car Loan", "start_date": "2023-01-01", "end_date": "2023-12-31", "balance": 1000},
        {"type": "Store Card", "start_date": "2023-03-01", "end_date": "2023-09-30", "balance": 500},
        {"type": "Home Loan", "start_date": "2023-04-01", "end_date": "2023-06-30", "balance": 800},
        {"type": "Store Card", "start_date": "2023-04-01", "end_date": "2023-07-30", "balance": 2000},
        {"type": "Store Card", "start_date": "2023-04-01", "end_date": "2023-09-30", "balance": 2000}
    ]

    time_windows = [1, 3, 6, 9, 12]

    try:
        results = process_liabilities(liabilities, time_windows)
        for months, start_date, balances, total_balance in results:
            print(f"\nLiabilities for the past {months} month(s) (from {start_date}):")
            for liability_type, balance in balances.items():
                print(f"  {liability_type}: ${balance:.2f}")
            print(f"  Total balance: ${total_balance:.2f}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()