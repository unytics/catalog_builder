SELECT
    TABLE_SCHEMA
    , COUNT(COMMENT)/COUNT(*) * 100 AS COLUMNS_COMMENTS_PERCENTAGE
FROM INFORMATION_SCHEMA.COLUMNS GROUP BY TABLE_SCHEMA;