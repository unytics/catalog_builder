# {{ name }} {% if schema.startswith('restricted_safe_') %}:lock:{% endif %}

<div class="grid cards" markdown>

-   - **Full name**: `{{ database }}.{{ schema }}.{{ name }}`
    - **Owner**: `{{ owner }}`
    - **Type**: `{{ type }}`
    {% if modified_at %}- **modified_at**: {{ modified_at }}{% endif %}
    {% if size %}- **size**: {{ size }}{% endif %}

-   **Description**

    {{ (description or '<span style="color: var(--md-default-fg-color--lighter);">No description</span>') | indent(4, false, true) }}

</div>



#### <span style="color:#fff">Details</span> { data-search-exclude }

=== "Columns"

    | Column | Type | Description |
    |---|---|---|
    {% for column in columns -%}
    | `{{ column.name }}` | `{{ column.type }}` | {{ column.comment }} |
    {% endfor %}

{% if raw_code %}
=== "SQL"

    ```sql
    {{ raw_code | indent(4, false, true) }}
    ```
{% endif %}
