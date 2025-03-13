import os

import pandas as pd
from snowflake.connector.cursor import SnowflakeCursor

HERE = os.path.dirname(os.path.abspath(__file__))

class Query:
    def __init__(query_name: str) -> str:
        with open(f"{HERE}/sql_queries/{query_name}.sql") as f:
            return f.read()
        
    def get_pandas_df_from_query(query: str, cur: SnowflakeCursor) -> pd.DataFrame:
        return cur.execute(query).fetch_pandas_all().to_dict(orient="index")