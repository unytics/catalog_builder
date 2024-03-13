# {{ name }}

<div class="grid cards" markdown>

-   - **Full name**: `{{ database }}.{{ schema }}.{{ name }}`
    - **Owner**: `{{ owner }}`
    - **Loader**: `{{ loader }}`
    - **Type**: `{{ type }}`
    {% if modified_at %}- **modified_at**: {{ modified_at }}{% endif %}
    {% if size %}- **size**: {{ size }}{% endif %}

-   **Description**

    {{ (description or '<span style="color: var(--md-default-fg-color--lighter);">No description</span>') | indent(4, false, true) }}

</div>



**Columns**

| Column | Type | Description |
|---|---|---|
{% for column in columns -%}
| `{{ column.name }}` | `{{ column.type }}` | {{ column.comment }} |
{% endfor %}

