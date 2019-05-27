from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, DateTime, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import numpy as np


engine = create_engine("mssql+pyodbc://bond:bond@10.28.7.43/InvestSystem?driver=SQL+Server")
Session = sessionmaker(bind=engine)
Base = declarative_base()


# 持仓类
class Position(Base):
    __tablename__ = 'AutoPosition'

    id = Column(Integer, primary_key=True)
    dt = Column(DateTime)
    direction = Column(Integer)
    code = Column(String(20))
    price = Column(DECIMAL(18, 5))
    volume = Column(Integer)

    def __init__(self, dt: datetime, direction: int, code: str, price: float, volume: int):
        self.dt = dt
        self.direction = direction
        self.code = code
        self.price = price
        self.volume = volume


# 订单类
class Order(Base):
    __tablename__ = 'OrderSignal'

    id = Column(Integer, primary_key=True)
    dt = Column(DateTime)
    direction = Column(Integer)
    code = Column(String(20))
    price = Column(DECIMAL(18, 5))
    volume = Column(Integer)
    cancel = Column(Integer)

    def __init__(self, dt: str, direction: int, code: str, price: float, volume: int, cancel: int = 0):
        self.dt = dt
        self.direction = direction
        self.code = code
        self.price = price
        self.volume = volume
        self.cancel = cancel

    def __str__(self):
        return "time:%s-direction:%d-code:%s-price:%f-volume:%d " % (
            self.dt, self.direction, self.code, self.price, self.volume)

    def __eq__(self, other):
        if np.all([self.direction == other.direction, self.code == other.code, round(self.price, 3) == round(other.price, 3),
                   self.volume == other.volume, self.cancel == other.cancel]):
            return True
        else:
            return False


if __name__ == '__main__':
    Base.metadata.create_all(engine)
