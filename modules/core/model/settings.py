from sqlalchemy.sql.expression import null
from sqlalchemy.sql.sqltypes import BIGINT, Boolean, DateTime
from modules.financing.crypto.dictionary import binance_order_books, bitso_order_books
from bot.brain import Base, session
from sqlalchemy import Column, String
from datetime import datetime


class Settings(Base):
    __tablename__ = "settings"
    id = Column(BIGINT, primary_key=True)  # CID user
    name = Column(String(300), nullable=False)
    current_market = Column(String(10), nullable=True)
    current_market_name = Column(String(30), nullable=True)
    current_platform = Column(String(20), nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column("created_at", DateTime, default=datetime.now())
    updated_at = Column("updated_at", DateTime, onupdate=datetime.now())

    def __init__(self, cid, name):
        self.id = cid
        self.name = name

    def __str__(self):
        text = self.name + " tus configuraciones son: \n\n"
        if self.is_verified:
            text = text + "* Tu cuenta está verificada \n\n"
        else:
            text = text + "* No se ha verificado tu cuenta \n\n"
        text = text + "* Tienes configurado " + self.current_market_name + " (" + self.current_market + ") " + " en la plataforma " + self.current_platform + " todas las operaciones se realizarán con esta configuración"

        return text


def update_settings(cid, name, current_market, verified):
    try:
        settings = Settings(cid, name)
        settings.current_market = current_market
        settings.is_verified = verified
        session.merge(settings)
        session.commit()
    except Exception as e:
        session.rollback()
        print("Error al guardar datos del usuario")
        print(e)


def get_settings(cid):
    try:
        return session.query(Settings).filter(Settings.id == cid).one()
    except Exception as e:
        session.rollback()
        print("Error al consultar datos")
        print(e)
    return null()


def update_market(cid, market, market_name, platform):
    settings = get_settings(cid)
    settings.current_market = market
    settings.current_market_name = market_name
    settings.current_platform = platform
    session.commit()
