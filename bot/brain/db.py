from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
load_dotenv()

url = 'mysql+mysqlconnector://'+os.environ['DB_USER']+':'+os.environ['DB_PASS']+'@'+os.environ['DB_HOST']+':3306/'+os.environ['DB_NAME']
engine = create_engine(url,echo=False)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()