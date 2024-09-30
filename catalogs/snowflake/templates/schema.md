# {{ SCHEMA_NAME }}

SCHEMA SIZE : `{{ KPI.SIZE }}`
SCHEMA TABLES COMMENT PERCENTAGE : `{{ KPI.TABLE_COMMENTS_PERCENTAGE }}`
SCHEMA COST : `{{ KPI.FAKE_SCHEMA_COST }}`


!!! info "Description"

    {{ (description or '<span style="color: var(--md-default-fg-color--lighter);">No description</span>') | indent(4, false, true) }}

-   - **Full name**: `{{ DATABASE_NAME }}.{{ SCHEMA_NAME }}`
    - **Owner**: `{{ SCHEMA_OWNER }}`
    - **Is transient**: `{{ IS_TRANSIENT }}`
    - **Is managed access**: `{{ IS_MANAGED_ACCESS }}`
    - **Retention time**: `{{ RETENTION_TIME }}`
    - **Schema creation**: `{{ SCHEMA_CREATION }}`
    - **Schema description**: `{{ SCHEMA_COMMENT }}`


**Tables**

| table | comment |
|---|---|
{% for table in TABLES -%}
| `{{ table.TABLE_NAME }}` | `{{table.TABLE_COMMENT}}` |
{% endfor -%}