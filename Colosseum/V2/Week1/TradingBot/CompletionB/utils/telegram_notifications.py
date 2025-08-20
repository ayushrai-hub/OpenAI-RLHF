from telegram import Bot
from telegram.ext import Updater
import asyncio

class TelegramNotifier:
    def __init__(self, token, chat_id):
        self.bot = Bot(token=token)
        self.chat_id = chat_id
        
    async def send_message(self, message):
        """Send message to Telegram"""
        await self.bot.send_message(
            chat_id=self.chat_id,
            text=message,
            parse_mode='HTML'
        )
        
    def send_order_notification(self, order):
        """Send order notification"""
        message = (
            f"🔔 New Order:\n"
            f"Symbol: {order['symbol']}\n"
            f"Type: {order['type']}\n"
            f"Side: {order['side']}\n"
            f"Price: {order['price']}\n"
            f"Amount: {order['amount']}\n"
            f"Status: {order['status']}"
        )
        
        asyncio.run(self.send_message(message))
