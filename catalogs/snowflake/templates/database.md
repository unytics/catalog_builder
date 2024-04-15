# {{ DATABASE_NAME }}

First KPI : 
`{{ DATABASE_COMMENTS_PERCENTAGE }}`
`{{ DATABASE_SIZE }}`
`{{ DATABASE_COMMENTS_PERCENTAGE }}`

-   - **Owner**: `{{ DATABASE_OWNER }}`
    - **Is transient**: `{{ IS_TRANSIENT }}`
    - **Database type**: `{{ DATABASE_TYPE }}`
    - **Retention time**: `{{ RETENTION_TIME }}`
    - **Database creation**: `{{ DATABASE_CREATION }}`
    - **Database description**: `{{ DATABASE_COMMENT }}`

**Schemas**

{% for schema in schemas %}
- [{{ schema }}]({{ schema }}/index.md)
{% endfor %}