---
hide:
  - toc
---

# {{ name | title }}

<div class="grid cards" markdown>

-   - **Full name**: `{{ database }}.{{ schema }}.{{ name }}`
    - **Owner**: `{{ metadata.owner }}`
    - **Type**: `{{ config.materialized }}`
    {% if stats and stats.last_modified %}- **modified_at**: {{ stats.last_modified.value }}{% endif %}
    {% if stats and stats.bytes %}- **bytes**: {{ stats.bytes.value }}{% endif %}

-   {% if tags %}- **Tags**: {% for tag in tags %}{% if not loop.first %}, {% endif %}`{{ tag }}`{% endfor %}{% endif %}
    {% if partition_by %}- **Partition by**: {{ partition_by }}{% endif %}
    {% if cluster_by %}- **Cluster by**: {{ cluster_by }}{% endif %}
    - **Description**

    {{ (description or '<span style="color: var(--md-default-fg-color--lighter);">No description</span>') | indent(4, false, true) }}

</div>




#### <span style="color:#fff">Details</span> { data-search-exclude }



=== "Columns"

    | Column | Type | Description |
    |---|---|---|
    {% for column in columns -%}
    | `{{ column.name }}` | `{{ column.type }}` | {{ column.description }} |
    {% endfor %}

{% if raw_code %}

=== "SQL"
    ```sql
    {{ raw_code | indent(4, false, true) }}
    ```
{% endif %}


=== "Depends On"

{% if depends_on and depends_on.nodes %}
    {% for node in depends_on.nodes -%}
    - `{{ node }}`
    {% endfor %}

{% endif %}

=== "Referenced By"

{% if ref_path is defined %}
    {% for ref in ref_path -%}
        {{ref}}
    {% endfor %}

{% endif %}
