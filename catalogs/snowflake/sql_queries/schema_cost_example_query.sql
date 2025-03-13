-- QUERY NEEDS A PROJECT THAT REALLY EXISTS. Example query to get the cost of a schema/table
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