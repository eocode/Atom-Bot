from sqlalchemy.sql.expression import null
from sqlalchemy.sql.sqltypes import BIGINT, Date, DateTime, Numeric
from data.db import Base, session
from sqlalchemy import Column, Integer, String, Float
from datetime import datetime


class Trade(Base):
    __tablename__ = "trade"
    id = Column(BIGINT, primary_key=True)
    market = Column(String(10), default="BTCMXN", nullable=False)
    date = Column(DateTime, default=datetime.now(), nullable=False)
    current_price = Column(Float(precision='10,2'), nullable=False)
    max_price = Column(Float(precision='10,2'), nullable=False)
    min_price = Column(Float(precision='10,2'), nullable=False)
    max_date = Column(DateTime, nullable=True)
    min_date = Column(DateTime, nullable=True)

    def __init__(
        self,
        date,
        market,
        current_price,
        max_price,
        min_price,
        max_date,
        min_date
    ):
        self.date = date
        self.market = market
        self.current_price = current_price
        self.max_price = max_price
        self.min_price = min_price
        self.max_date = max_date
        self.min_date = min_date

    def __repr__(self):
        return f"BTC({self.date}, {self.current_price})"

    def __str__(self):
        return str(self.date)


def save_current_price(
    date,
    market,
    current_price,
    max_price,
    min_price,
    max_date=null(),
    min_date=null()
):
    trade = Trade(
        date,
        market,
        current_price,
        max_price,
        min_price,
        max_date,
        min_date
    )
    session.add(trade)
    session.commit()


def get_value(price):
    consulta = session.query(Trade).filter(Trade.current_price < price).count()
    print(consulta)

def get_last_trade():
    consulta = session.query(Trade).order_by(Trade.id.desc()).first()
    return (consulta.max_price, consulta.min_price)