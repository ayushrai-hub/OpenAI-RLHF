# ideal_completion.py

import logging
import pandas as pd

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FinancialAnalytics:

    def __init__(self):
        # Initialize any necessary class variables or settings here
        pass

    # Helper to create methods dynamically
    def _create_method(self, method_id, column_id, calc_func, *args):
        def method(self):
            try:
                result = calc_func(self, column_id, *args)
                if pd.isna(result):
                    result = 0.0
                return result
            except Exception as e:
                logging.error(f"Error in {method_id} for column {column_id}: {e}")
                return None

        return method

    # Common calculation method for numeric values with error handling
    def _calc_column_total(self, column_id):
        try:
            # Insert your calculation logic here, for example, summing a column
            return 100  # Placeholder for the actual calculation process
        except Exception as e:
            logging.error(f"Error calculating total for {column_id}: {e}")
            return None

    # Common formatting function
    @staticmethod
    def format(value, type):
        # Different formatting based on the type (currency, percentage, etc.)
        if type == "currency":
            return f"${value:,.2f}"
        elif type == "percentage":
            return f"{value:.2f}%"
        else:
            return value

    # Main method generator
    def create_methods(self, attributes, intervals, conditions, durations, cycles, discrepancy=False, percentage=False):
        for attribute in attributes:
            for interval in intervals:
                for condition in conditions:
                    if condition == 'estimate' and interval == 'last_year':
                        continue  # Skip unneeded combinations

                    for duration in durations:
                        for cycle in cycles:
                            attribute_type = "capacity" if attribute == "quantity" else "value"
                            method_id = f'{attribute}_{interval}_{cycle}_{duration}_{condition}_raw'
                            column_id = f'{attribute}_{interval}_{cycle}_{duration}_{condition}_{attribute_type}'

                            if discrepancy:
                                column_id2 = f'{attribute}_{interval}_{cycle}_{duration}_budget_{attribute_type}'
                                calc_func = self._calc_variance
                                bound_func = self._create_method(method_id, column_id, calc_func, column_id2)
                            elif percentage:
                                column_id2 = f'{attribute}_{interval}_{cycle}_{duration}_{condition}_{attribute_type}'
                                calc_func = self._calc_percentage
                                bound_func = self._create_method(method_id, column_id, calc_func, column_id2)
                            else:
                                calc_func = self._calc_column_total
                                bound_func = self._create_method(method_id, column_id, calc_func)

                            # Dynamically attach the method to the class
                            setattr(FinancialAnalytics, method_id, bound_func)
                            logging.info(f"Created method {method_id}")

    def _calc_variance(self, column_id, column_id2):
        try:
            actual_val = pd.to_numeric(self._calc_column_total(column_id), errors='coerce')
            budget_val = pd.to_numeric(self._calc_column_total(column_id2), errors='coerce')
            return actual_val - budget_val
        except Exception as e:
            logging.error(f"Error calculating variance for {column_id} and {column_id2}: {e}")
            return None

    def _calc_percentage(self, column_id, column_id2):
        try:
            actual_val = pd.to_numeric(self._calc_column_total(column_id), errors='coerce')
            budget_val = pd.to_numeric(self._calc_column_total(column_id2), errors='coerce')
            percentage = 0 if budget_val == 0 else ((actual_val - budget_val) / budget_val) * 100
            return percentage
        except Exception as e:
            logging.error(f"Error calculating percentage for {column_id} and {column_id2}: {e}")
            return None