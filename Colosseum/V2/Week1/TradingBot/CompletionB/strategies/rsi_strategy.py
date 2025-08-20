from .base_strategy import BaseStrategy
import pandas as pd
import ta

class RSIStrategy(BaseStrategy):
    def __init__(self, config):
        self.period = config['period']
        self.overbought = config['overbought']
        self.oversold = config['oversold']
        
    def generate_signal(self, df: pd.DataFrame) -> str:
        """Generate trading signal based on RSI"""
        df['RSI'] = ta.momentum.RSIIndicator(
            close=df['close'], 
            window=self.period
        ).rsi()
        
        current_rsi = df['RSI'].iloc[-1]
        
        if current_rsi <= self.oversold:
            return 'buy'
        elif current_rsi >= self.overbought:
            return 'sell'
        else:
            return 'hold'
