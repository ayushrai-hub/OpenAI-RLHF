# binance_bot.py

import ccxt
import time
import pandas as pd
from config import *
from indicators import analyze_technicals
from utils import setup_logger, calculate_trade_amount, get_current_time

logger = setup_logger()

def create_exchange():
    return ccxt.binance({
        'apiKey': API_KEY,
        'secret': API_SECRET,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'future'  # Use futures market
        }
    })

def fetch_ohlcv(exchange, symbol, timeframe):
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=100)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df
    except Exception as e:
        logger.error(f"Error fetching OHLCV data for {symbol}: {e}")
        return None

def place_order(exchange, symbol, side, amount, stop_loss=None, take_profit=None):
    try:
        order = exchange.create_market_order(symbol, side, amount)
        logger.info(f"Placed {side} order for {amount} {symbol}")
        
        if stop_loss:
            sl_order = exchange.create_stop_loss_order(symbol, 'sell', amount, stop_loss)
            logger.info(f"Placed stop-loss order at {stop_loss}")
        
        if take_profit:
            tp_order = exchange.create_take_profit_order(symbol, 'sell', amount, take_profit)
            logger.info(f"Placed take-profit order at {take_profit}")
        
        return order
    except Exception as e:
        logger.error(f"Error placing order for {symbol}: {e}")
        return None

def trading_logic(exchange, symbol):
    df = fetch_ohlcv(exchange, symbol, TIMEFRAME)
    if df is None:
        return
    
    analysis = analyze_technicals(df, RSI_PERIOD, MACD_FAST, MACD_SLOW, MACD_SIGNAL)
    
    current_price = analysis['close']
    rsi = analysis['rsi']
    macd = analysis['macd']
    signal = analysis['signal']
    lower_bb = analysis['lower_bb']
    upper_bb = analysis['upper_bb']
    
    # Trading logic based on indicators
    if rsi < RSI_OVERSOLD and current_price < lower_bb and macd > signal:
        # Bullish signal
        amount = calculate_trade_amount(exchange, symbol, TRADE_AMOUNT)
        stop_loss = current_price * (1 - STOP_LOSS_PERCENTAGE)
        take_profit = current_price * (1 + TAKE_PROFIT_PERCENTAGE)
        place_order(exchange, symbol, 'buy', amount, stop_loss, take_profit)
    elif rsi > RSI_OVERBOUGHT and current_price > upper_bb and macd < signal:
        # Bearish signal
        amount = calculate_trade_amount(exchange, symbol, TRADE_AMOUNT)
        stop_loss = current_price * (1 + STOP_LOSS_PERCENTAGE)
        take_profit = current_price * (1 - TAKE_PROFIT_PERCENTAGE)
        place_order(exchange, symbol, 'sell', amount, stop_loss, take_profit)
    else:
        logger.info(f"No trading signal for {symbol} at {get_current_time()}")

def main():
    exchange = create_exchange()
    
    while True:
        try:
            for symbol in TRADING_PAIRS:
                trading_logic(exchange, symbol)
            
            time.sleep(UPDATE_INTERVAL)
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            time.sleep(60)  # Wait for 1 minute before trying again

if __name__ == "__main__":
    main()
