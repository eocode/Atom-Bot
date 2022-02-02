from sqlalchemy.sql.sqltypes import BIGINT, Boolean, DateTime
from bot.brain import Base, session
from sqlalchemy import Column, String
from datetime import datetime
from sqlalchemy.orm import relationship


class Account(Base):
    __tablename__ = "account"
    id = Column(BIGINT, primary_key=True)  # CID user

    name = Column(String(300), nullable=False)
    current_market = Column(String(10), nullable=True)
    current_market_name = Column(String(30), nullable=True)
    current_platform = Column(String(20), nullable=True)
    speak = Column(Boolean, default=False, nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False)

    created_at = Column("created_at", DateTime, default=datetime.now())
    updated_at = Column("updated_at", DateTime, onupdate=datetime.now())

    positions = relationship("Position", back_populates="account")

    def __init__(self, cid, name):
        self.id = cid
        self.name = name

    def __str__(self):
        if self.current_market_name:
            text = self.name + " tus configuraciones son: \n\n"
            if self.is_verified:
                text = text + "* Tu cuenta está verificada \n\n"
            else:
                text = text + "* No se ha verificado tu cuenta \n\n"
            text = text + "* Tienes configurado " + self.current_market_name + " (" + self.current_market + ") " + " en la plataforma " + self.current_platform + " todas las operaciones se realizarán con esta configuración \n\n"
            if self.speak:
                text = text + "* Tienes activadas las funciones de reproducción"
        else:
            text = "Lo sentimos, primero debe configurar su cuenta mediante el comando \n /configurar_mercado"
        return text


def update_settings(cid, name, current_market, verified):
    try:
        account = Account(cid, name)
        account.current_market = current_market
        account.is_verified = verified
        session.merge(account)
        session.commit()
    except Exception as e:
        session.rollback()
        print("Error al guardar datos del usuario")
        print(e)


def get_settings(cid):
    try:
        session.expire_all()
        return session.query(Account).filter(Account.id == cid).one()
    except Exception as e:
        session.rollback()
        print("Error al consultar datos de la cuenta")
        print(e)
    return None


def update_market(cid, market, market_name, platform):
    account = get_settings(cid)
    account.current_market = market
    account.current_market_name = market_name
    account.current_platform = platform
    session.commit()
