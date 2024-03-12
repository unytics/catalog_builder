# {{ name }}

<nav class="level">
  <div class="level-item has-text-centered">
    <div>
      <p class="heading">Last modified at</p>
      <p class="title">{{ last_modified_at }}</p>
    </div>
  </div>
  <div class="level-item has-text-centered">
    <div>
      <p class="heading">Created at</p>
      <p class="title">{{ created_at }}</p>
    </div>
  </div>
  <div class="level-item has-text-centered">
    <div>
      <p class="heading">Nb Rows</p>
      <p class="title">{{ row_count }}</p>
    </div>
  </div>
  <div class="level-item has-text-centered">
    <div>
      <p class="heading">Size</p>
      <p class="title">{{ size }}</p>
    </div>
  </div>
</nav>

---

**Description**

{{ (description or '<span style="color: var(--md-default-fg-color--lighter);">No description</span>') | indent(4, false, true) }}


[Open in BigQuery :material-open-in-new:](https://console.cloud.google.com/bigquery?ws=!1m5!1m4!4m3!1sbigquery-public-data!2s{{ dataset }}!3s{{ name }})

[Open in Looker Studio :material-open-in-new:](javascript:openLookerStudio\(\);) *(:warning: this costs you a full scan of some columns)*



---

**Columns**

| Column | Type | Description |
|---|---|---|
{% for column in columns -%}
| `{{ column.name }}` | `{{ column.data_type }}` | {{ column.description }} |
{% endfor %}




<script>
function openLookerStudio() {

  if (!localStorage.billingBigQueryProject) {
    localStorage.billingBigQueryProject = prompt('To open Looker Studio, please enter your BigQuery Billing Project');
  }
  const url = `https://lookerstudio.google.com/u/0/reporting/create?c.mode=edit&c.source=BQ_UI&ds.type=TABLE&ds.connector=BIG_QUERY&ds.billingProjectId=${localStorage.billingBigQueryProject}&ds.projectId=bigquery-public-data&ds.tableId={{ name }}&ds.datasetId={{ dataset }}&ds.sqlType=STANDARD_SQL`;
  window.open(url);

}
</script>