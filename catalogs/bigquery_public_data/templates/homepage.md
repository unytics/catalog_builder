# BigQuery Public Datasets

!!! info "Description"
    
    Catalog of all active BigQuery Public Tables (*ie tables from [bigquery-public-data](https://cloud.google.com/bigquery/public-data#public-ui) project which have been updated during the latest 30 months*)


**Datasets**

{% for dataset in datasets %}
- [{{ dataset }}]({{ dataset }}/index.md)
{% endfor %}