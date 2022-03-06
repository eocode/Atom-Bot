import pandas as pd
import sqlalchemy
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
import os

load_dotenv()

Base = declarative_base()
metadata = Base.metadata


class SQLConnector:

    def __init__(self):
        url = 'mysql+pymysql://' + os.environ['DB_USER'] + ':' + os.environ['DB_PASS'] + '@' + os.environ[
            'DB_HOST'] + ':3306/' + os.environ['DB_NAME']
        self.engine = create_engine(url, echo=False, pool_pre_ping=True, pool_recycle=3600,
                                    isolation_level="READ UNCOMMITTED")
        self.connection = self.engine.connect()
        session_maker = sessionmaker(bind=self.engine)
        self.session = session_maker()
        Base.metadata.create_all(self.engine)

    def __str__(self):
        return "Conexión establecida"

    def run_query(self, query):
        try:
            if query != "":
                return self.connection.execute(sqlalchemy.text(query))
            else:
                return None
        except Exception as e:
            print("Error: ", query, e)
            return None

    def run_pandas_query(self, query):
        try:
            if query != "":
                return pd.read_sql_query(sqlalchemy.text(query), con=self.connection)
            else:
                return None
        except Exception as e:
            print("Error: ", query, e)
            print('----------------------')
            return None

    def save_pandas_to_db_and_replace(self, dataframe, table, schema):
        dataframe.to_sql(name=table, schema=schema, index=False, con=self.engine, if_exists='replace',
                         method="multi")

    def save_pandas_to_database(self, dataframe, table, schema, output_columns, exists='append'):
        dataframe.to_sql(name=table, schema=schema,
                         if_exists=exists, index=False, con=self.connection, method="multi", dtype=output_columns)
