from sqlalchemy.sql.sqltypes import BIGINT, Boolean, DateTime

from sqlalchemy import Column, String
from datetime import datetime

from modules.core.data.bot_system import system
from connect.sql_connector import Base


class Account(Base):
    __tablename__ = "account"
    id = Column(BIGINT, primary_key=True)  # CID user

    name = Column(String(300), nullable=False)
    current_crypto = Column(String(5), nullable=True)
    current_pair = Column(String(5), nullable=True)
    current_market = Column(String(10), nullable=True)
    current_market_name = Column(String(30), nullable=True)
    current_platform = Column(String(20), nullable=True)
    speak = Column(Boolean, default=False, nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_group = Column(Boolean, default=False, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)

    created_at = Column("created_at", DateTime, default=datetime.now())
    updated_at = Column("updated_at", DateTime, onupdate=datetime.now())

    def __init__(self, cid, name):
        self.id = cid
        self.name = name

    def __str__(self):
        if self.is_group:
            text = self.name + "\n\n"
            if self.is_verified:
                text = text + "* El grupo está habilitado para recibir notificaciones\n\n"
            else:
                text = text + "* No se ha verificado el uso del bot en este grupo \n\n"
        else:
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


def update_settings(cid, name, verified, group):
    try:
        account = Account(cid, name)
        account.is_verified = verified
        account.is_group = group
        system('sql').session.merge(account)
        system('sql').session.commit()
    except Exception as e:
        system('sql').session.rollback()
        print("Error al guardar datos del usuario")
        print(e)


def get_accounts():
    try:
        system('sql').session.expire_all()
        return system('sql').session.query(Account).filter(Account.is_verified == 1).all()
    except Exception as e:
        system('sql').session.rollback()
        print("Error al consultar cuentas activas")
        print(e)
    return None


def get_groups():
    try:
        system('sql').session.expire_all()
        return system('sql').session.query(Account).filter(Account.is_group == 1, Account.is_verified == 1).all()
    except Exception as e:
        system('sql').session.rollback()
        print("Error al consultar grupos activos")
        print(e)
    return None


def get_settings(cid):
    try:
        system('sql').session.expire_all()
        return system('sql').session.query(Account).filter(Account.id == cid).one()
    except Exception as e:
        system('sql').session.rollback()
        print("Error al consultar datos de la cuenta")
        print(e)
    return None


def update_market(cid, crypto, pair, market, market_name, platform):
    account = get_settings(cid)
    account.current_crypto = crypto
    account.current_pair = pair
    account.current_market = market
    account.current_market_name = market_name
    account.current_platform = platform
    system('sql').session.commit()
