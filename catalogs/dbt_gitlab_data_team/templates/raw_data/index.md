# Raw Data 

All raw data will still be in the `RAW` database in Snowflake. These raw tables are referred to as `source tables` or `raw tables`. They are typically stored in a schema that indicates its original data source, e.g. `netsuite`

Sources are defined in dbt using a `sources.yml` file.