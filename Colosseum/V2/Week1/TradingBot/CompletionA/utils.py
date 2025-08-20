# utils.py

import logging
from datetime import datetime

def setup_logger():
    logger = logging.getLogger('BinanceBot')
    logger.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    file_handler = logging.FileHandler('binance_bot.log')
    file_handler.setFormatter(formatter)
    
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    
    return logger

def calculate_trade_amount(exchange, symbol, usdt_amount):
    ticker = exchange.fetch_ticker(symbol)
    price = ticker['last']
    return usdt_amount / price

def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
