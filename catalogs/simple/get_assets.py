import os
import json 

import pandas as pd
import google.cloud.bigquery

PROJECT = 'bigquery-public-data'
HERE = os.path.dirname(os.path.abspath(__file__))

DATASET_TABLES_QUERY = '''
with


----------------------------------------
--             SOURCES                --
----------------------------------------
tables as (
  select 
    dataset_id || '.' || table_id as table,
    *,
  from {project}.{dataset}.__TABLES__
),

table_descriptions as (
  select
    table_schema || '.' || table_name as table,
    regexp_extract(option_value, '^"(.*)"$') as description,
  from {project}.{dataset}.INFORMATION_SCHEMA.TABLE_OPTIONS
  where option_name = 'description'
),

columns as (
  select
    field_path as name,
    table_schema || '.' || table_name as table,
    data_type,
    ifnull(description, '') as description,
  from {project}.{dataset}.INFORMATION_SCHEMA.COLUMN_FIELD_PATHS
),

columns_details as (
  select
    column_name as name,
    table_schema || '.' || table_name as table,
    ordinal_position,
    is_partitioning_column = 'YES' as is_partitioning_column,
  from {project}.{dataset}.INFORMATION_SCHEMA.COLUMNS
),


----------------------------------------
--              JOINS                 --
----------------------------------------

columns_joined as (
  select *
  from columns
  left join columns_details using(table, name)
),

paritioning_columns as (
  select 
    table, 
    name as partitioning_column,
  from columns_joined
  where is_partitioning_column
),

table_columns as (
  select 
    table, 
    array_agg((select as struct columns_joined.* except(table, ordinal_position, is_partitioning_column)) order by ordinal_position) as columns
  from columns_joined
  group by table
),

tables_joined as (
  select
    *,
  from tables
  left join table_descriptions using(table)
  left join table_columns using(table)
  left join paritioning_columns using(table)
)


----------------------------------------
--              FINAL                 --
----------------------------------------
select 
  'table' as asset_type,
  replace(table, '.', '/') as path,
  struct(
    table_id as name,
    string(date(timestamp_millis(creation_time))) as created_at,
    string(date(timestamp_millis(last_modified_time))) as last_modified_at,
    format("%'d", row_count) as row_count,
    case 
      when size_bytes / pow(2, 40) > 1 then format('%.2f TB', size_bytes / pow(2, 40))
      when size_bytes / pow(2, 30) > 1 then format('%.2f GB', size_bytes / pow(2, 30))
      else format('%.2f MB', size_bytes / pow(2, 20))
    end as size,
    type,
    ifnull(description, '') as description,
    ifnull(partitioning_column, '') as partitioning_column,
    columns
  ) as data,
from tables_joined


'''


bigquery = google.cloud.bigquery.Client()
datasets = bigquery.list_datasets(PROJECT)

with open(f'{HERE}/tmp_assets.jsonl', 'w', encoding='utf-8') as out:
    for dataset in datasets:
        dataset_id = dataset.dataset_id
        print(dataset_id)
        try:
            dataset = bigquery.get_dataset(f'{PROJECT}.{dataset_id}')
        except:
            print(f'COULD NOT GET DATASET {dataset_id}')
            continue
        try:
            tables = bigquery.query(DATASET_TABLES_QUERY.format(project=PROJECT, dataset=dataset_id)).result()
        except:
            print(f'COULD NOT GET TABLES FOR DATASET {dataset_id}')
            continue
        tables = [dict(t) for t in tables]
        dataset = {
            'asset_type': 'dataset', 
            'path': f'{dataset_id}/index',
            'data': {
                'name': dataset_id, 
                'description': dataset.description or '',
                'tables': [
                    {k: v for k, v in table['data'].items() if k != 'columns'}
                    for table in tables
                ],
            }
        }
        assets = [dataset] + tables
        content = '\n'.join([json.dumps(asset) for asset in assets])
        out.write(content + '\n')


df = pd.read_json(f'{HERE}/tmp_assets.jsonl', lines=True)
df.to_parquet(f'{HERE}/assets.parquet')