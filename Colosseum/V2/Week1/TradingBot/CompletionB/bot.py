import ccxt
import pandas as pd
import numpy as np
from datetime import datetime
import time
from typing import Dict, List
import yaml
import os
from dotenv import load_dotenv

from utils.logger import setup_logger
from utils.telegram_notifications import TelegramNotifier
from utils.database import Database
from strategies.moving_average import MovingAverageStrategy
from strategies.rsi_strategy import RSIStrategy

class TradingBot:
    def __init__(self):
        # Load configuration
        self.load_config()
        
        # Setup logger
        self.logger = setup_logger()
        
        # Initialize exchange
        self.setup_exchange()
        
        # Initialize database
        self.db = Database(self.config['database']['url'])
        
        # Setup telegram notifications
        if self.config['telegram']['enabled']:
            self.notifier = TelegramNotifier(
                self.config['telegram']['bot_token'],
                self.config['telegram']['chat_id']
            )
        
        # Initialize strategies
        self.setup_strategies()
        
        # Initialize trading state
        self.active_trades = {}
        
    def load_config(self):
        """Load configuration from yaml file"""
        load_dotenv()
        with open('config/config.yaml', 'r') as file:
            self.config = yaml.safe_load(file)
            
        # Replace environment variables
        self.config['exchange']['api_key'] = os.getenv('BINANCE_API_KEY')
        self.config['exchange']['api_secret'] = os.getenv('BINANCE_API_SECRET')
        
    def setup_exchange(self):
        """Initialize exchange connection"""
        exchange_class = getattr(ccxt, self.config['exchange']['name'])
        self.exchange = exchange_class({
            'apiKey': self.config['exchange']['api_key'],
            'secret': self.config['exchange']['api_secret'],
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future' if self.config['exchange']['testnet'] else 'spot'
            }
        })
        
        if self.config['exchange']['testnet']:
            self.exchange.set_sandbox_mode(True)
            
    def setup_strategies(self):
        """Initialize trading strategies"""
        self.strategies = {}
        
        if self.config['strategies']['moving_average']['enabled']:
            self.strategies['ma'] = MovingAverageStrategy(
                self.config['strategies']['moving_average']
            )
            
        if self.config['strategies']['rsi']['enabled']:
            self.strategies['rsi'] = RSIStrategy(
                self.config['strategies']['rsi']
            )
            
    def fetch_ohlcv(self, symbol: str, timeframe: str = '1h') -> pd.DataFrame:
        """Fetch OHLCV data from exchange"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            self.logger.error(f"Error fetching OHLCV data: {e}")
            return None
            
    def calculate_position_size(self, symbol: str) -> float:
        """Calculate position size based on account balance and risk parameters"""
        try:
            balance = self.exchange.fetch_balance()
            usdt_balance = balance['total']['USDT']
            position_size = (usdt_balance * self.config['trading']['position_size_percentage']) / 100
            return min(position_size, self.config['trading']['base_order_size_usdt'])
        except Exception as e:
            self.logger.error(f"Error calculating position size: {e}")
            return None
            
    def place_order(self, symbol: str, side: str, amount: float, price: float = None):
        """Place order on exchange"""
        try:
            order_type = 'market' if price is None else 'limit'
            order = self.exchange.create_order(
                symbol=symbol,
                type=order_type,
                side=side,
                amount=amount,
                price=price
            )
            
            # Store order in database
            self.db.store_order(order)
            
            # Send notification
            if self.config['telegram']['enabled']:
                self.notifier.send_order_notification(order)
                
            return order
        except Exception as e:
            self.logger.error(f"Error placing order: {e}")
            return None
            
    def manage_trades(self):
        """Manage open trades and check for exit conditions"""
        for symbol in self.active_trades:
            trade = self.active_trades[symbol]
            current_price = self.exchange.fetch_ticker(symbol)['last']
            
            # Check stop loss
            if trade['side'] == 'buy':
                if current_price <= trade['stop_loss']:
                    self.close_position(symbol, 'sell', trade['amount'])
                elif current_price >= trade['take_profit']:
                    self.close_position(symbol, 'sell', trade['amount'])
                    
    def close_position(self, symbol: str, side: str, amount: float):
        """Close an open position"""
        try:
            order = self.place_order(symbol, side, amount)
            if order:
                del self.active_trades[symbol]
                self.logger.info(f"Closed position for {symbol}")
        except Exception as e:
            self.logger.error(f"Error closing position: {e}")
            
    def run(self):
        """Main bot loop"""
        self.logger.info("Starting trading bot...")
        
        while True:
            try:
                for symbol in self.config['trading']['symbols']:
                    # Fetch latest data
                    df = self.fetch_ohlcv(symbol)
                    if df is None:
                        continue
                        
                    # Check if we can open new trades
                    if (len(self.active_trades) < self.config['trading']['max_open_trades'] 
                        and symbol not in self.active_trades):
                        
                        # Get signals from all strategies
                        signals = []
                        for strategy in self.strategies.values():
                            signal = strategy.generate_signal(df)
                            signals.append(signal)
                            
                        # If all strategies agree on a signal
                        if all(s == 'buy' for s in signals):
                            position_size = self.calculate_position_size(symbol)
                            if position_size:
                                order = self.place_order(symbol, 'buy', position_size)
                                if order:
                                    current_price = df['close'].iloc[-1]
                                    self.active_trades[symbol] = {
                                        'side': 'buy',
                                        'amount': position_size,
                                        'entry_price': current_price,
                                        'stop_loss': current_price * (1 - self.config['trading']['stop_loss_percentage'] / 100),
                                        'take_profit': current_price * (1 + self.config['trading']['take_profit_percentage'] / 100)
                                    }
                                    
                # Manage existing trades
                self.manage_trades()
                
                # Sleep for a while
                time.sleep(60)
                
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                time.sleep(60)

if __name__ == "__main__":
    bot = TradingBot()
    bot.run()
