import os

import pandas as pd
import snowflake.connector

# TODO : charger de la donnée dans le snowflake pour voir si on a qqc et si c'est un pb côté code ou côté warehouse
# TODO : comprendre pourquoi les calculs ne se font pas bien
# TODO : sauvegarder la mise en place du compte
DATABASE = "FINANCE__ECONOMICS"
SNOWFLAKE_ROLE = "CATALOG_BUILDER_ROLE"
VIRTUAL_WAREHOUSE = "CATALOG_BUILDER_WH"
HERE = os.path.dirname(os.path.abspath(__file__))
CHAR_TO_REPLACE_NEW_LINE = " "

DATABASES_QUERY = """
SELECT 
    DATABASE_NAME, 
    DATABASE_OWNER, 
    IS_TRANSIENT,
    COMMENT AS DATABASE_COMMENT, 
    CREATED AS DATABASE_CREATION, 
    RETENTION_TIME, 
    TYPE AS DATABASE_TYPE
FROM INFORMATION_SCHEMA.DATABASES;
"""

SCHEMAS_QUERY = """
SELECT 
    CATALOG_NAME AS DATABASE_NAME,
    SCHEMA_NAME,
    SCHEMA_OWNER,
    IS_TRANSIENT,
    IS_MANAGED_ACCESS,
    RETENTION_TIME,
    CREATED AS SCHEMA_CREATION,
    COMMENT AS SCHEMA_COMMENT
FROM INFORMATION_SCHEMA.SCHEMATA;
"""

TABLES_QUERY = """
SELECT 
    TABLE_CATALOG AS DATABASE_NAME,
    TABLE_SCHEMA,
    TABLE_NAME,
    TABLE_OWNER,
    TABLE_TYPE,
    IS_TRANSIENT,
    CLUSTERING_KEY,
    ROW_COUNT,
    BYTES,
    RETENTION_TIME,
    CREATED AS TABLE_CREATION,
    LAST_ALTERED AS LAST_MODIFICATION,
    LAST_DDL AS LAST_STRUCTURE_CHANGE,
    LAST_DDL_BY AS LAST_STRUCTURE_CHANGER,
    COMMENT AS TABLE_COMMENT,
    IS_TEMPORARY
FROM INFORMATION_SCHEMA.TABLES;
"""

COLUMNS_QUERY = """
SELECT
    TABLE_CATALOG AS TABLE_DATABASE,
    TABLE_SCHEMA,
    TABLE_NAME,
    COLUMN_NAME,
    IS_NULLABLE,
    IS_IDENTITY,
    DATA_TYPE,
    CHARACTER_MAXIMUM_LENGTH,
    CHARACTER_OCTET_LENGTH,
    NUMERIC_PRECISION,
    NUMERIC_PRECISION_RADIX,
    NUMERIC_SCALE,
    DATETIME_PRECISION,
    INTERVAL_TYPE,
    COMMENT
FROM INFORMATION_SCHEMA.COLUMNS 
ORDER BY 
    TABLE_CATALOG,
    TABLE_SCHEMA,
    TABLE_NAME,
    COLUMN_NAME,
    ORDINAL_POSITION;
"""

# TODO : faire une requête qui sort le coût des requêtes d'un schéma par jour
SCHEMA_METADATA_QUERY = """
SELECT 
    TABLE_SCHEMA
    , SUM(BYTES) AS SIZE
    , COUNT(COMMENT)/COUNT(*) * 100 AS TABLE_COMMENTS_PERCENTAGE
    , 0 AS FAKE_SCHEMA_COST
FROM INFORMATION_SCHEMA.TABLES GROUP BY TABLE_SCHEMA;
"""

TABLE_METADATA_QUERY = """
SELECT
    TABLE_SCHEMA
    , COUNT(COMMENT)/COUNT(*) * 100 AS COLUMNS_COMMENTS_PERCENTAGE
FROM INFORMATION_SCHEMA.COLUMNS GROUP BY TABLE_SCHEMA;
"""

# SCHEMA_COST = """ QUERY NEEDS A PROJECT THAT REALLY """ Example query to get the cost of a schema/table
"""
WITH table_names (table_name) AS(
    SELECT TABLE_NAME from information_schema.tables WHERE table_schema='TESTS_FINOPS'
),
used_tables (
    QUERY_ID,
    accessed_object,
    QUERY_START_TIME,
    direct_objects_accessed_name,
    objects_modified_name,
    base_objects_accessed_name
) AS (
    select 
        QUERY_ID,
        DIRECT_OBJECTS_ACCESSED[0]."objectName" as accessed_object,
        QUERY_START_TIME,
        direct_objects_accessed_flattened.VALUE:objectName as direct_objects_accessed_name,
        objects_modified_flattened.VALUE:objectName as objects_modified_name,
        base_objects_accessed_flattened.VALUE:objectName as base_objects_accessed_name
    from snowflake.account_usage.access_history,
        LATERAL FLATTEN(input => snowflake.account_usage.access_history.DIRECT_OBJECTS_ACCESSED, outer=> true) direct_objects_accessed_flattened,
        LATERAL FLATTEN(input => snowflake.account_usage.access_history.OBJECTS_MODIFIED, outer=> true) objects_modified_flattened,
        LATERAL FLATTEN(input => snowflake.account_usage.access_history.BASE_OBJECTS_ACCESSED, outer=> true) base_objects_accessed_flattened
        WHERE NOT IS_NULL_VALUE(direct_objects_accessed_flattened.VALUE:objectName) 
            OR NOT IS_NULL_VALUE(objects_modified_flattened.VALUE:objectName) AND objects_modified_flattened.VALUE:objectName!='WORKSHEETS_APP.PUBLIC.BLOBS'
            OR NOT IS_NULL_VALUE(base_objects_accessed_flattened.VALUE:objectName)
),
query_price (
    QUERY_ID,
    QUERY_TEXT,
    CREDITS_USED_CLOUD_SERVICES,
    QUERY_TYPE,
    SESSION_ID,
    USER_NAME,
    ROLE_NAME,
    WAREHOUSE_ID,
    WAREHOUSE_NAME,
    START_TIME,
    END_TIME,
    COMPILATION_TIME,
    EXECUTION_TIME
) AS (
    SELECT
        QUERY_ID,
        QUERY_TEXT,
        CREDITS_USED_CLOUD_SERVICES,
        QUERY_TYPE,
        SESSION_ID,
        USER_NAME,
        ROLE_NAME,
        WAREHOUSE_ID,
        WAREHOUSE_NAME,
        START_TIME,
        END_TIME,
        COMPILATION_TIME,
        EXECUTION_TIME
    FROM snowflake.account_usage.query_history
    WHERE true
      --AND start_time >= TIMESTAMPADD(day, -1, CURRENT_TIMESTAMP)
      AND SCHEMA_NAME='TESTS_FINOPS'
      AND QUERY_TYPE!='SHOW' 
)
SELECT 
    table_names.TABLE_NAME,
    used_tables.QUERY_ID,
    accessed_object,
    QUERY_START_TIME,
    direct_objects_accessed_name,
    objects_modified_name,
    base_objects_accessed_name,
    QUERY_TEXT,
    CREDITS_USED_CLOUD_SERVICES,
    QUERY_TYPE,
    SESSION_ID,
    USER_NAME,
    ROLE_NAME,
    WAREHOUSE_ID,
    WAREHOUSE_NAME,
    START_TIME,
    END_TIME,
    COMPILATION_TIME,
    EXECUTION_TIME
FROM table_names
INNER JOIN used_tables ON
    CONTAINS(used_tables.direct_objects_accessed_name, table_names.TABLE_NAME)
    OR CONTAINS(used_tables.objects_modified_name, table_names.TABLE_NAME)
    OR CONTAINS(used_tables.base_objects_accessed_name, table_names.TABLE_NAME)    
INNER JOIN query_price ON used_tables.QUERY_ID=query_price.QUERY_ID;


SELECT COMMENT FROM COLUMNS WHERE COMMENT IS NULL or COMMENT='';
"""


conn = snowflake.connector.connect(
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    role=SNOWFLAKE_ROLE,
    database=DATABASE,
    warehouse=VIRTUAL_WAREHOUSE,
)
cur = conn.cursor()



def get_pandas_df_from_query(query: str) -> pd.DataFrame:
    return cur.execute(query).fetch_pandas_all().to_dict(orient="index")


db_data, schemas_data, tables_data, columns_data = map(
    lambda query: get_pandas_df_from_query(query),
    [DATABASES_QUERY, SCHEMAS_QUERY, TABLES_QUERY, COLUMNS_QUERY],
)

# TODO : refacto le code ci-dessous

# TODO : FAIRE UNE VERSION PLUS SIMPLE PUIS FAIRE UNE VERSION JOLIE

schema_metadata = (
    cur.execute(SCHEMA_METADATA_QUERY).fetch_pandas_all().to_dict(orient="index")
)
table_metadata = (
    cur.execute(TABLE_METADATA_QUERY).fetch_pandas_all().to_dict(orient="index")
)


for table in tables_data.values():
    table["COLUMNS"] = [
        column
        for column in columns_data.values()
        if column.get("TABLE_NAME") == table.get("TABLE_NAME")
    ]
    table["TABLE_COMMENT"] = table.get("TABLE_COMMENT").replace(
        "\n", CHAR_TO_REPLACE_NEW_LINE
    )

    table["COLUMNS"] = map(
        lambda colonne: colonne.get("COMMENT", "").replace(
            "\n", CHAR_TO_REPLACE_NEW_LINE
        ),
        table["COLUMNS"],
    )

for schema in schemas_data.values():
    schema["TABLES"] = [
        {
            "TABLE_NAME": table.get("TABLE_NAME"),
            "TABLE_COMMENT": table.get("TABLE_COMMENT"),
        }
        for table in tables_data.values()
        if table.get("TABLE_SCHEMA") == schema.get("SCHEMA_NAME")
    ]

    schema["SCHEMA_COMMENT"] = str(schema.get("SCHEMA_COMMENT") or "").replace(
        "\n", CHAR_TO_REPLACE_NEW_LINE
    )

    schema["KPI"] = [
        {
            "SIZE": schema_metadata.get("SIZE"),
            "TABLE_COMMENTS_PERCENTAGE": schema_metadata.get("TABLE_COMMENTS_PERCENTAGE"),
            "FAKE_SCHEMA_COST": schema_metadata.get("FAKE_SCHEMA_COST"),
        }
        for schema_metadata in schema_metadata.values()
        if schema_metadata.get("TABLE_SCHEMA") == schema.get("SCHEMA_NAME")
    ][0]

print(schema)

for database in db_data.values():
    database["SCHEMAS"] = [
        {
            "SCHEMA_NAME": schema.get("SCHEMA_NAME"),
            "SCHEMA_COMMENT": schema.get("SCHEMA_COMMENT"),
        }
        for schema in schemas_data.values()
        if schema.get("DATABASE_NAME") == database.get("DATABASE_NAME")
    ]
    database["DATABASE_COMMENT"] = str(database.get("DATABASE_COMMENT") or "").replace(
        "\n", CHAR_TO_REPLACE_NEW_LINE
    )

databases = [
    {
        "asset_type": "database",
        "path": f"{database.get('DATABASE_NAME')}/index",
        "data": database,
    }
    for database in db_data.values()
]
schemas = [
    {
        "asset_type": "schema",
        "path": f"{schema.get('DATABASE_NAME')}/{schema.get('SCHEMA_NAME')}/index",
        "data": schema,
    }
    for schema in schemas_data.values()
]
tables = [
    {
        "asset_type": "table",
        "path": f"{table.get('DATABASE_NAME')}/{table.get('TABLE_SCHEMA')}/{table.get('TABLE_NAME')}/index",
        "data": table,
    }
    for table in tables_data.values()
]
columns = [
    {
        "asset_type": "column",
        "path": f"{column.get('DATABASE_NAME')}/{column.get('TABLE_SCHEMA')}/{column.get('TABLE_NAME')}/{column.get('COLUMN_NAME')}/index",
        "data": column,
    }
    for column in columns_data.values()
]

# TODO : faire ça avec un map ?

for table in tables:
    table["data"]["LAST_MODIFICATION"] = str(table["data"].get("LAST_MODIFICATION"))
    table["data"]["TABLE_CREATION"] = str(table["data"].get("LAST_MODIFICATION"))
    table["data"]["LAST_STRUCTURE_CHANGE"] = str(
        table["data"].get("LAST_STRUCTURE_CHANGE")
    )
    table["data"]["COLUMNS"] = list(table["data"].get("COLUMNS"))
    # print(json.dumps(table, indent=4))

df = pd.concat(
    [
        pd.DataFrame(databases),
        pd.DataFrame(schemas),
        pd.DataFrame(tables),
        pd.DataFrame(columns),
    ]
)
df.to_parquet(f"{HERE}/assets.parquet")
