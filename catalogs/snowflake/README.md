# Create the environment to test this catalog for Snowflake

- Create a Snowflake account if you don't have one yet by going here : https://signup.snowflake.com/
- Get the data from cybersin by going here : https://app.snowflake.com/marketplace/listing/GZTSZAS2KF7/snowflake-data-finance-economics?search=finance%20economics
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

-- Test d'accès aux tables
SELECT * FROM finance__economics.INFORMATION_SCHEMA.TABLES LIMIT 10;

-- Test d'utilisation du datawarehouse
USE WAREHOUSE X_SMALL;
```

- Create your venv using these commands : 
```
python -m venv my_venv_name
source my_venv_name/bin/activate
pip install -r [PATH_TO_REQUIREMNT_FILE]
```

- Create your catalog assets using this command : 
```
python3 catalogs/snowflake/generate_assets_file.py
```

- Launch your data catalog and serve it using this command : 
```
catalog build-and-serve snowflake --port 9000
```