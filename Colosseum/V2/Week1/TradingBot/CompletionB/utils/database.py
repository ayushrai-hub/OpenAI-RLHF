from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String)
    order_id = Column(String)
    timestamp = Column(DateTime)
    type = Column(String)
    side = Column(String)
    price = Column(Float)
    amount = Column(Float)
    status = Column(String)

class Database:
    def __init__(self, url):
        self.engine = create_engine(url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
    def store_order(self, order_data):
        """Store order information in database"""
        session = self.Session()
        
        order = Order(
            symbol=order_data['symbol'],
            order_id=str(order_data['id']),
            timestamp=datetime.fromtimestamp(order_data['timestamp']/1000),
            type=order_data['type'],
            side=order_data['side'],
            price=float(order_data['price']),
            amount=float(order_data['amount']),
            status=order_data['status']
        )
        
        session.add(order)
        session.commit()
        session.close()
