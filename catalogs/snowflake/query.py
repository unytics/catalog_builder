import os

import pandas as pd
from snowflake.connector.cursor import SnowflakeCursor

HERE = os.path.dirname(os.path.abspath(__file__))

class Query:
    def __init__(self, query_name: str, cur: SnowflakeCursor) -> str:
        self.cur = cur
        with open(f"{HERE}/sql_queries/{query_name}.sql") as f:
            self.query = f.read()
        
    def get_pandas_df_from_query(self) -> pd.DataFrame:
        return self.cur.execute(self.query).fetch_pandas_all().to_dict(orient="index")