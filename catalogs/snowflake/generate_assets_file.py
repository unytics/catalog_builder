import configparser
import os
from typing import Dict

import pandas as pd
import snowflake.connector
from query import Query

HERE = os.path.dirname(os.path.abspath(__file__))

config = configparser.ConfigParser()
config.read(f'{HERE}/catalog_conf.ini')
DATABASE = config['database']['name']
SNOWFLAKE_ROLE = config['database']['role']
VIRTUAL_WAREHOUSE = config['database']['warehouse_name']

CHAR_TO_REPLACE_NEW_LINE = ' '

def fix_comment(comment: str) -> str:
    return comment.replace("\n", CHAR_TO_REPLACE_NEW_LINE)

def add_columns_to_table(table: Dict, columns_data: Dict) -> None:
    table["COLUMNS"] = [
        column
        for column in columns_data.values()
        if column.get("TABLE_NAME") == table.get("TABLE_NAME")
    ]

def fix_columns_comments(table: Dict) -> None:
    # fixing comments
    for column in table["COLUMNS"]:
        column["COMMENT"] = column["COMMENT"].replace(
            "\n", CHAR_TO_REPLACE_NEW_LINE
        )


def add_tables_to_schema(schema: Dict, tables_data: Dict) -> None:
    schema["TABLES"] = [
            {
                "TABLE_NAME": table.get("TABLE_NAME"),
                "TABLE_COMMENT": table.get("TABLE_COMMENT"),
            }
            for table in tables_data.values()
            if table.get("TABLE_SCHEMA") == schema.get("SCHEMA_NAME")
        ]

def add_schema_kpi(schema: Dict, schema_metadata: Dict) -> None:
    schema["KPI"] = [
            {
                "SIZE": schema_metadata.get("SIZE"),
                "TABLE_COMMENTS_PERCENTAGE": schema_metadata.get("TABLE_COMMENTS_PERCENTAGE"),
                "FAKE_SCHEMA_COST": schema_metadata.get("FAKE_SCHEMA_COST"),
            }
            for schema_metadata in schema_metadata.values()
            if schema_metadata.get("TABLE_SCHEMA") == schema.get("SCHEMA_NAME")
        ][0]
    
def add_database_schemas(database: Dict, schemas_data: Dict) -> None:
    database["SCHEMAS"] = [
            {
                "SCHEMA_NAME": schema.get("SCHEMA_NAME"),
                "SCHEMA_COMMENT": schema.get("SCHEMA_COMMENT"),
            }
            for schema in schemas_data.values()
            if schema.get("DATABASE_NAME") == database.get("DATABASE_NAME")
        ]

def get_database_path(database: Dict) -> str:
    return f"{database.get('DATABASE_NAME')}/index"

def get_schema_path(schema: Dict) -> str:
    return f"{schema.get('DATABASE_NAME')}/{schema.get('SCHEMA_NAME')}/index"

def get_table_path(table: Dict) -> str:
    return f"{table.get('DATABASE_NAME')}/{table.get('TABLE_SCHEMA')}/{table.get('TABLE_NAME')}/index"

def get_column_path(column: Dict) -> str:
    return f"{column.get('DATABASE_NAME')}/{column.get('TABLE_SCHEMA')}/{column.get('TABLE_NAME')}/{column.get('COLUMN_NAME')}/index"


if __name__ == "__main__":
    conn = snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        role=SNOWFLAKE_ROLE,
        database=DATABASE,
        warehouse=VIRTUAL_WAREHOUSE,
    )
    cur = conn.cursor()

    queries_to_get = ["databases_query", "schemas_query", "tables_query", "columns_query", "schema_metadata_query", "table_metadata_query"]
    queries_list = [Query(query_file, cur) for query_file in queries_to_get]
    db_data, schemas_data, tables_data, columns_data, schema_metadata, table_metadata = map(
        lambda query: query.get_pandas_df_from_query(),
        queries_list,
    )

    for table in tables_data.values():
        add_columns_to_table(table, columns_data)
        fix_columns_comments(table)
        table["TABLE_COMMENT"] = fix_comment(table.get("TABLE_COMMENT"))

    for schema in schemas_data.values():
        add_tables_to_schema(schema, tables_data)
        add_schema_kpi(schema, schema_metadata)
        schema["SCHEMA_COMMENT"] = fix_comment(str(schema.get("SCHEMA_COMMENT") or ""))
    
    for database in db_data.values():
        add_database_schemas(database, schemas_data)
        database["DATABASE_COMMENT"] = fix_comment(str(database.get("DATABASE_COMMENT") or ""))

    

    


    databases = [
        {
            "asset_type": "database",
            "path": get_database_path(database),
            "data": database,
        }
        for database in db_data.values()
    ]

    schemas = [
        {
            "asset_type": "schema",
            "path": get_schema_path(schema),
            "data": schema,
        }
        for schema in schemas_data.values()
    ]
    tables = [
        {
            "asset_type": "table",
            "path": get_table_path(table),
            "data": table,
        }
        for table in tables_data.values()
    ]
    columns = [
        {
            "asset_type": "column",
            "path": get_column_path(column),
            "data": column,
        }
        for column in columns_data.values()
    ]

    # TODO : faire ça avec un map ?
    # TODO : comprendre ce que fait le str là-dedans
    # TODO : fix le table creation ?
    # TODO : comprendre les 3 premières lignes car elles sont un peu bizarres

    for table in tables:
        table["data"]["LAST_MODIFICATION"] = str(table["data"].get("LAST_MODIFICATION"))
        table["data"]["TABLE_CREATION"] = str(table["data"].get("LAST_MODIFICATION"))
        table["data"]["LAST_STRUCTURE_CHANGE"] = str(
            table["data"].get("LAST_STRUCTURE_CHANGE")
        )
        table["data"]["COLUMNS"] = list(table["data"].get("COLUMNS"))

    df = pd.concat(
        [
            pd.DataFrame(databases),
            pd.DataFrame(schemas),
            pd.DataFrame(tables),
            pd.DataFrame(columns),
        ]
    )
    df.to_parquet(f"{HERE}/assets.parquet")

"""for schema in schemas_data.values():
        schema["TABLES"] = [
            {
                "TABLE_NAME": table.get("TABLE_NAME"),
                "TABLE_COMMENT": table.get("TABLE_COMMENT"),
            }
            for table in tables_data.values()
            if table.get("TABLE_SCHEMA") == schema.get("SCHEMA_NAME")
        ]
        # TODO : check ce que ça fait et ce qu'il se passe si on change ce get
        schema["SCHEMA_COMMENT"] = fix_comment(str(schema.get("SCHEMA_COMMENT") or ""))

        schema["KPI"] = [
            {
                "SIZE": schema_metadata.get("SIZE"),
                "TABLE_COMMENTS_PERCENTAGE": schema_metadata.get("TABLE_COMMENTS_PERCENTAGE"),
                "FAKE_SCHEMA_COST": schema_metadata.get("FAKE_SCHEMA_COST"),
            }
            for schema_metadata in schema_metadata.values()
            if schema_metadata.get("TABLE_SCHEMA") == schema.get("SCHEMA_NAME")
        ][0]
        
        for database in db_data.values():
        database["SCHEMAS"] = [
            {
                "SCHEMA_NAME": schema.get("SCHEMA_NAME"),
                "SCHEMA_COMMENT": schema.get("SCHEMA_COMMENT"),
            }
            for schema in schemas_data.values()
            if schema.get("DATABASE_NAME") == database.get("DATABASE_NAME")
        ]
        database["DATABASE_COMMENT"] = fix_comment(str(database.get("DATABASE_COMMENT") or ""))"""