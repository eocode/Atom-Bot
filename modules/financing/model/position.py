from sqlalchemy.sql.sqltypes import BIGINT, DateTime, Boolean
from bot.brain import Base, session
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Float, Integer, ForeignKey
from datetime import datetime


class Position(Base):
    __tablename__ = "position"

    id = Column(BIGINT, primary_key=True)

    market = Column(String(10), nullable=False)
    account_id = Column(BIGINT, ForeignKey('account.id'))
    account = relationship("Account", back_populates="positions")

    transaction_type = Column(String(10), nullable=False)

    price = Column(Float(precision='10,2'), nullable=False)
    comission = Column(Float(precision='10,2'), nullable=False)
    cuantity = Column(Float(precision='10,2'), nullable=False)

    is_open = Column(Boolean, default=True, nullable=False)

    created_at = Column("created_at", DateTime, default=datetime.now())
    updated_at = Column("updated_at", DateTime, onupdate=datetime.now())

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


def get_position(position_id):
    query = session.query(Position).filter(Position.id < position_id).count()
    return query
