# Create the environment to test this catalog for Snowflake

# To recreate the same example 
- Create a Snowflake account if you don't have one yet by going here : https://signup.snowflake.com/
- Get the data from cybersin by going here : https://app.snowflake.com/marketplace/listing/[YOUR_ACCOUNT]/snowflake-data-finance-economics?search=finance%20economics
- Create the proper service accounts and roles by adapting and launching these commands for example :
```
CREATE ROLE SERVICE_ACCOUNT_CATALOG_BUILDER;

CREATE USER SERVICE_ACCOUNT_CATALOG_BUILDER 
    PASSWORD = 'YOUR_PASSWORD_HERE' 
    DEFAULT_ROLE = SERVICE_ACCOUNT_CATALOG_BUILDER 
    MUST_CHANGE_PASSWORD = FALSE;

GRANT ROLE SERVICE_ACCOUNT_CATALOG_BUILDER TO USER SERVICE_ACCOUNT_CATALOG_BUILDER;

GRANT IMPORTED PRIVILEGES ON DATABASE finance__economics TO ROLE SERVICE_ACCOUNT_CATALOG_BUILDER;

CREATE WAREHOUSE X_SMALL 
    WITH 
    WAREHOUSE_SIZE = 'X-SMALL' 
    AUTO_SUSPEND = 60 
    AUTO_RESUME = TRUE 
    INITIALLY_SUSPENDED = TRUE;

GRANT USAGE ON WAREHOUSE X_SMALL TO ROLE SERVICE_ACCOUNT_CATALOG_BUILDER;

GRANT ROLE SERVICE_ACCOUNT_CATALOG_BUILDER TO ROLE ACCOUNTADMIN;

-- Test tables access
SELECT * FROM finance__economics.INFORMATION_SCHEMA.TABLES LIMIT 10;

-- Test warehouse access
USE WAREHOUSE X_SMALL;
```

# To use catalog builder for Snowflake

## Create your venv using these commands : 
```
python -m venv my_venv_name
source my_venv_name/bin/activate
pip install -r [PATH_TO_REQUIREMNT_FILE]
```

## Create your catalog assets using this command : 
```
python3 catalogs/snowflake/generate_assets_file.py
```

### Script config
- The script configuration is meant to be set in the catalog_conf.ini file and is read at the beginning of the Python script. It should contain at least the following values : 
    - database.name : the name of the database to connect to. Your service account should have rights granted at least to this database and all the other databases it wants to document 
    - database.role : the role your service account should use to get databases descriptions
    - database.warehouse_name : the name of the warehouse your service account will use to do the compute
- Secrets, however are meant to be set in environment variables as follows :
    - SNOWFLAKE_USER : contains the name of the Snowflake service account
    - SNOWFLAKE_PASSWORD : contains the password used to connect to the Snowflake account
    - SNOWFLAKE_ACCOUNT : the identifier of your Snowflake account

### How does it work ?
This script works by running the following queries against the Snowflake account : 
- databases_query : gets informations about the databases
- schemas_query : gets informations about the schemas
- tables_query : gets informations about the tables
- columns_query : gets informations about the columns
- schema_metadata_query : gets informations such as tables sizes and percentage of commented tables for each schema
- table_metadata_query : gets informations such as percentage of commented columns for each table
These queries can be found and customized in the sql_queries folder. 

Once these queries are run, we join some results, such as schemas_query's result and schemas_metadata_query's result to create 3 datasets : the databases dataset, the schemas dataset and the tables (which includes data for the tables' columns as well)

After this, we write our data at the proper format to be readable by the data catalog and the script is done.

### What are the expected outputs ?
This script should write a file named assets.parquet

## Launch your data catalog and serve it using this command : 
```
catalog build-and-serve snowflake --port 9000
```
