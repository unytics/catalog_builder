# {{ table_name }}

<div class="grid cards" markdown>

- **Full name**: `{{ DATABASE_NAME }}.{{ TABLE_SCHEMA }}.{{ TABLE_NAME }}`
- **Owner**: `{{ TABLE_OWNER }}`
- **Type**: `{{ TABLE_TYPE }}`
- **Is transient**: `{{ IS_TRANSIENT }}`
- **Clustering key**: `{{ CLUSTERING_KEY }}`
- **Number of rows**: `{{ ROW_COUNT }}`
- **Volume**: `{{ BYTES }}`
- **Retention time**: `{{ RETENTION_TIME }}`
- **Table creation**: `{{ TABLE_CREATION }}`
- **Last modification**: `{{ LAST_MODIFICATION }}`
- **Last table structure change**: `{{ LAST_STRUCTURE_CHANGE }}`
- **Last table structure changer**: `{{ LAST_STRUCTURE_CHANGER }}`
- **Table description**: `{{ TABLE_COMMENT }}`
- **Is table temporary**: `{{ IS_TEMPORARY }}`

</div>



#### <span style="color:#fff">Details</span> { data-search-exclude }

=== "Columns"

    | Column | Type | Description |
    |---|---|---|
    {% for column in COLUMNS -%}
    | `{{ column.COLUMN_NAME }}` | `{{ column.DATA_TYPE }}` | `{{ column.COMMENT }}` | `{{ column.IS_NULLABLE }}` | `{{ column.IS_IDENTITY }}` |
    {% endfor %}

{% if raw_code %}
=== "SQL"

    ```sql
    {{ raw_code | indent(4, false, true) }}
    ```
{% endif %}
