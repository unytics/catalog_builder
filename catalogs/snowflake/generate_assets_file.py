import configparser
import os

import pandas as pd
import snowflake.connector

# TODO : sauvegarder la mise en place du compte
# CONNECTING TO DATABASE
# TODO : virer ça dans la classe de chargement de la donnée ? eventuellement, le mettre en tant que connecteur et faire une inversion de dépendance ?
# TODO : virer la partie database etc dans un fichier de conf du script --> un fichier .env pour pouvoir y mettre les mdp etc ?
# TODO : comprendre pourquoi est-ce que ce code n'est pas lancé quand on lance le build and serve et ce qui est lancé à sa place
# TODO : faire en sorte que le taf soit fait sur plusieurs databases et non une seule
# TODO : faire en sorte que les créations d'assets soient faites dans des classes spécifiques avec des fonction utilitaires et virer ce code dégueulasse d'ici 

HERE = os.path.dirname(os.path.abspath(__file__))

config = configparser.ConfigParser()
config.read(f'{HERE}/catalog_conf.ini')
DATABASE = config['database']['name']
SNOWFLAKE_ROLE = config['database']['role']
VIRTUAL_WAREHOUSE = config['database']['warehouse_name']

CHAR_TO_REPLACE_NEW_LINE = config['metadata']['char_to_replace_new_line']

conn = snowflake.connector.connect(
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    role=SNOWFLAKE_ROLE,
    database=DATABASE,
    warehouse=VIRTUAL_WAREHOUSE,
)
cur = conn.cursor()

# Running queries

# TODO : transform this as objects with get query as the __init__ and the get_pandas_df_from_query as a method
def get_query(query_name:str) -> str:
    with open(f"{HERE}/sql_queries/{query_name}.sql") as f:
        return f.read()

def get_pandas_df_from_query(query: str) -> pd.DataFrame:
    return cur.execute(query).fetch_pandas_all().to_dict(orient="index")

# TODO : faire ça avec une comprehension list ?
queries_to_get = ["databases_query", "schemas_query", "tables_query", "columns_query", "schema_metadata_query", "table_metadata_query"]
queries_list = [get_query(query_file) for query_file in queries_to_get]
db_data, schemas_data, tables_data, columns_data, schema_metadata, table_metadata = map(
    lambda query: get_pandas_df_from_query(query),
    queries_list,
)
"""DATABASES_QUERY = get_query("databases_query")

SCHEMAS_QUERY = get_query("schemas_query")

TABLES_QUERY = get_query("tables_query")

COLUMNS_QUERY = get_query("columns_query")

SCHEMA_METADATA_QUERY = get_query("schema_metadata_query")

TABLE_METADATA_QUERY = get_query("table_metadata_query")

queres_list = [
    DATABASES_QUERY,
    SCHEMAS_QUERY,
    TABLES_QUERY,
    COLUMNS_QUERY,
    SCHEMA_METADATA_QUERY,
    TABLE_METADATA_QUERY,
]

db_data, schemas_data, tables_data, columns_data, schema_metadata, table_metadata = map(
    lambda query: get_pandas_df_from_query(query),
    queres_list,
)
"""

# TODO : refacto le code ci-dessous

# TODO : FAIRE UNE VERSION PLUS SIMPLE PUIS FAIRE UNE VERSION JOLIE

#TODO : virer ça dans le map du dessus et faire une liste avec les 6 requêtes directement ?

# transformaing data to fit the catalog's format
def fix_comment(comment: str) -> str:
    return comment.replace("\n", CHAR_TO_REPLACE_NEW_LINE)


for table in tables_data.values():
    table["COLUMNS"] = [
        column
        for column in columns_data.values()
        if column.get("TABLE_NAME") == table.get("TABLE_NAME")
    ]
    table["TABLE_COMMENT"] = fix_comment(table.get("TABLE_COMMENT"))

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
    database["DATABASE_COMMENT"] = fix_comment(str(database.get("DATABASE_COMMENT") or ""))

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
