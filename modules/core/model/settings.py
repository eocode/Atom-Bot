from sqlalchemy.sql.expression import null
from sqlalchemy.sql.sqltypes import BIGINT, Boolean, DateTime
from bot.brain import Base, session
from sqlalchemy import Column, String
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

    def __str__(self):
        text = self.name + " tus configuraciones son: \n"
        text = text + "Mercado: " + self.current_market + "\n"
        text = text + "Cuenta verificada: " + ("Sí" if self.is_verified else "No")
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


def update_market(cid, current_market):
    settings = get_settings(cid)
    settings.current_market = current_market
    session.commit()
