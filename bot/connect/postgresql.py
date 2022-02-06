import pandas as pd
import sqlalchemy
from dotenv import load_dotenv
from bot.brain import engine

load_dotenv()


class Connections:
    engine = None
    connection = None
    table = ""
    schema = ""

    def __init__(self, table, schema):
        self.engine = engine
        self.connection = engine.connect()
        self.table = table
        self.schema = schema

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

    def save_pandas_to_db_and_replace(self, dataframe):
        dataframe.to_sql(name=self.table, schema=self.schema, index=False, con=self.engine, if_exists='replace',
                         method="multi")

    def save_pandas_to_database(self, dataframe, output_columns, exists='append'):
        dataframe.to_sql(name=self.table, schema=self.schema,
                         if_exists=exists, index=False, con=self.connection, method="multi", dtype=output_columns)