# indicators.py

import pandas as pd
import numpy as np
import talib

def get_rsi(data, period=14):
    return talib.RSI(data['close'], timeperiod=period)

def get_macd(data, fast_period=12, slow_period=26, signal_period=9):
    macd, signal, _ = talib.MACD(data['close'], fastperiod=fast_period, slowperiod=slow_period, signalperiod=signal_period)
    return macd, signal

def get_bollinger_bands(data, period=20, num_std=2):
    upper, middle, lower = talib.BBANDS(data['close'], timeperiod=period, nbdevup=num_std, nbdevdn=num_std)
    return upper, middle, lower

def analyze_technicals(data, rsi_period, macd_fast, macd_slow, macd_signal):
    rsi = get_rsi(data, rsi_period)
    macd, signal = get_macd(data, macd_fast, macd_slow, macd_signal)
    upper, middle, lower = get_bollinger_bands(data)
    
    last_close = data['close'].iloc[-1]
    last_rsi = rsi.iloc[-1]
    last_macd = macd.iloc[-1]
    last_signal = signal.iloc[-1]
    last_lower_bb = lower.iloc[-1]
    last_upper_bb = upper.iloc[-1]
    
    return {
        'rsi': last_rsi,
        'macd': last_macd,
        'signal': last_signal,
        'lower_bb': last_lower_bb,
        'upper_bb': last_upper_bb,
        'close': last_close
    }
