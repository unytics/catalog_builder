# {{ name }}

!!! info "Description"

    {{ (description or '<span style="color: var(--md-default-fg-color--lighter);">No description</span>') | indent(4, false, true) }}


**Tables**

| table | infos |
|---|---|
{% for table in tables -%}
| [{{ table.name }}]({{ table.name }}.md)<br>{{ table.description }} | **Last modified at**: {{ table.last_modified_at }}<br>**Nb Rows**: {{ table.row_count }}<br>**Size**: {{ table.size }}<br>**Is partitioned**: {{ table.partition_column != '' }}<br>**Created at**:{{ table.created_at }} |
{% endfor -%}