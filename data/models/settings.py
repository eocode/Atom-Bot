from sqlalchemy.sql.expression import null
from sqlalchemy.sql.sqltypes import BIGINT, Boolean, Date, DateTime, Numeric
from data.db import Base, session
from sqlalchemy import Column, Integer, String, Float
from datetime import datetime


class Settings(Base):
    __tablename__ = "settings"
    id = Column(BIGINT, primary_key=True)  # CID user
    name = Column(String(300), nullable=False)
    current_market = Column(String(10), nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column("created_at", DateTime, default=datetime.now())
    updated_at = Column("updated_at", DateTime, onupdate=datetime.now())

    def __init__(self, cid, name):
        self.id = cid
        self.name = name

    def __repr__(self):
        return str(self.current_market)

    def __str__(self):
        return str(self.current_market)


def update_settings(cid, name, current_market, verified):
    settings = Settings(cid, name)
    settings.current_market = current_market
    settings.is_verified = verified
    session.merge(settings)
    session.commit()


def get_market(cid):
    return (
        session.query(Settings)
        .filter(Settings.id < cid)
        .order_by(Settings.id.desc())
        .first()
    )
