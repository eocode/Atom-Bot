from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from binance.client import Client
import os

load_dotenv()

url = 'mysql+mysqlconnector://' + os.environ['DB_USER'] + ':' + os.environ['DB_PASS'] + '@' + os.environ[
    'DB_HOST'] + ':3306/' + os.environ['DB_NAME']
engine = create_engine(url, echo=False)
conn = engine.connect()
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

binance_client = Client(api_key=os.environ['binance_api_key'], api_secret=os.environ['binance_api_secret'])
binsizes = {"1m": 1, "5m": 5, "1h": 60, "4h": 240, "1d": 1440}
