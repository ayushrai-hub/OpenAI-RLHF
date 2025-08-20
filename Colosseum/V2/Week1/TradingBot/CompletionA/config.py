# config.py

# Binance API credentials
API_KEY = 'your_binance_api_key'
API_SECRET = 'your_binance_api_secret'

# Trading pairs
TRADING_PAIRS = ['BTC/USDT', 'ETH/USDT', 'ADA/USDT']

# Trade amount in USDT
TRADE_AMOUNT = 50

# Technical indicator parameters
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

# Risk management
STOP_LOSS_PERCENTAGE = 0.05  # 5%
TAKE_PROFIT_PERCENTAGE = 0.1  # 10%

# Timeframe for analysis
TIMEFRAME = '1h'  # 1 hour candles

# How often to run the main loop (in seconds)
UPDATE_INTERVAL = 300  # 5 minutes
