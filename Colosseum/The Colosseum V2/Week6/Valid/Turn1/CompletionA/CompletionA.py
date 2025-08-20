from langchain_community.tools import tool
import yfinance as yf
import pandas as pd
from datetime import datetime

#@tool('Fetch historical cryptocurrency prices')
def get_historical_data(data_requests: list):
    """
    Fetch historical price data for one or more cryptocurrency symbols
    between specified start and end dates or for a specific date.
    
    **Parameters**:
    - `data_requests` (list): A list of dictionaries, each containing the following keys:
    - `symbol` (str): Symbol of the cryptocurrency, in the format '<symbol>-USD' (e.g., 'BTC-USD').
    - `start_date` (str, optional): Start date in 'YYYY-MM-DD' format.
    - `end_date` (str, optional): End date in 'YYYY-MM-DD' format.
    - `date` (str, optional): Specific date in 'YYYY-MM-DD' format to be used if `start_date` and `end_date` are not provided.
    - `period` (str, optional): Period of time to fetch historical data for, in '1d', '5d', '1wk', '1mo', '3mo',
    '6mo', '1y', '4y', '10y' format. Defaults to '1d'.
    
    **Returns**:
    - `dict`: Historical price data for the specified cryptocurrency symbols
    in a dictionary format or an error message if an error occurs.
    """
    result = {}
    try:
        for request in data_requests:
            symbol = request.get('symbol')
            start_date = request.get('start_date')
            end_date = request.get('end_date')
            date = request.get('date')
            period = request.get('period', '1d')

            # Handle cases where 'date' is provided instead of 'start_date' and 'end_date'
            if not start_date or not end_date:
                if date:
                    start_date = date
                    end_date = date
                else:
                    raise ValueError("Either 'start_date' and 'end_date' or 'date' must be provided")

            # Get daily data
            data = yf.download(symbol, start=start_date, end=end_date, interval='1d')
            close_data = data['Close']

            # Resample data based on the period
            if period == '1d':
                resampled_data = close_data
            else:
                # Convert end_date to datetime for comparison
                end_date_dt = pd.to_datetime(end_date)
                last_available_date = close_data.index[-1]

                if period == '5d':
                    resampled_data = close_data.resample('5D').ffill()
                elif period == '1wk':
                    resampled_data = close_data.resample('W').ffill()
                elif period == '1mo':
                    # First, resample to complete months
                    monthly_data = close_data.resample('M').ffill()
                    # If the end_date is mid-month, append the current partial month
                    if end_date_dt.day > 1 and end_date_dt.month == last_available_date.month:
                        current_month_start = pd.Timestamp(year=end_date_dt.year, 
                                                        month=end_date_dt.month, 
                                                        day=1)
                        partial_month_data = close_data[current_month_start:last_available_date]
                        if not partial_month_data.empty:
                            monthly_data = pd.concat([monthly_data, 
                                                    pd.Series(partial_month_data[-1:], 
                                                            index=[last_available_date])])
                    resampled_data = monthly_data
                elif period == '3mo':
                    resampled_data = close_data.resample('Q').ffill()
                elif period == '6mo':
                    resampled_data = close_data.resample('6M').ffill()
                elif period == '1y':
                    resampled_data = close_data.resample('Y').ffill()
                elif period == '4y':
                    resampled_data = close_data.resample('4A').ffill()
                elif period == '10y':
                    resampled_data = close_data.resample('10A').ffill()
                else:
                    resampled_data = close_data

                # Cap the final timestamp at the most recent date available
                resampled_data = resampled_data[resampled_data.index <= last_available_date]

            result[symbol] = resampled_data.to_dict() if not resampled_data.empty else None
    except Exception as e:
        return {"error": str(e)}
    
    return result

# Example usage:
if __name__ == "__main__":
    # Test with current date (mid-month scenario)
    today = datetime.now().strftime('%Y-%m-%d')
    ohlcv = get_historical_data([{'symbol': "BTC-USD", 
                                'start_date': "2024-01-01", 
                                'end_date': today, 
                                'period': "1mo"}])
    print(ohlcv)
