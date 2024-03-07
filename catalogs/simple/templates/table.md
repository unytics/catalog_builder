# {{ name }}

!!! info "Description"

    {{ (description or '<span style="color: var(--md-default-fg-color--lighter);">No description</span>') | indent(4, false, true) }}


<div class="grid cards" markdown>

-   **Columns**

    ---
    
    | Column | Type | Description |
    |---|---|---|
    {% for column in columns -%}
    | `{{ column.name }}` | `{{ column.data_type }}` | {{ column.description }} |
    {% endfor %}


-   **Infos**

    ---

    |  |   |
    |---|---|
    | **Last modified at** | {{ last_modified_at }} |
    | **Created at** |{{ created_at }} |
    | **Nb Rows** | {{ row_count }} |
    | **Size** | {{ size }} |
    | **Is partitioned** | {{ partition_column != '' }} |

</div>


