from .base_strategy import BaseStrategy
import pandas as pd

class MovingAverageStrategy(BaseStrategy):
    def __init__(self, config):
        self.short_window = config['short_window']
        self.long_window = config['long_window']
        
    def generate_signal(self, df: pd.DataFrame) -> str:
        """Generate trading signal based on moving average crossover"""
        df['SMA_short'] = df['close'].rolling(window=self.short_window).mean()
        df['SMA_long'] = df['close'].rolling(window=self.long_window).mean()
        
        # Generate signals
        if df['SMA_short'].iloc[-1] > df['SMA_long'].iloc[-1] and \
           df['SMA_short'].iloc[-2] <= df['SMA_long'].iloc[-2]:
            return 'buy'
        elif df['SMA_short'].iloc[-1] < df['SMA_long'].iloc[-1] and \
             df['SMA_short'].iloc[-2] >= df['SMA_long'].iloc[-2]:
            return 'sell'
        else:
            return 'hold'
