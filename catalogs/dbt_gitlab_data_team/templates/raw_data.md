---
search:
  exclude: true
---

# Raw Data

**Ingested Raw Data**. They are defined as sources in dbt and belong to `RAW` database.


<div class="grid cards" markdown>

-   **Schemas**

    {% for schema in schemas %}
    - [{{ schema }}]({{ schema }}/index.md)
    {% endfor %}

</div>
