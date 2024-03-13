import json
import os
import urllib.request
import datetime

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))

MANIFEST_FILE = f'{HERE}/tmp_manifest.json'
CATALOG_FILE = f'{HERE}/tmp_catalog.json'

COMMON_COLUMNS = ['database', 'schema', 'name', 'type', 'description', 'created_at', 'owner', 'size', 'last_modified', 'columns']
ASSET_TYPES = {
    'source': {
        'path': lambda df: 'Raw Data/' + df['schema'] + '/' + df['name'],
        'data_columns': COMMON_COLUMNS + ['loader'],
    },
    'node': {
        'path': lambda df: (
            df['database'].replace({'RAW': 'Raw Data', 'PREP': 'Source Models', 'PROD': 'Models'}) + '/' + 
            df['schema'].str.replace('restricted_safe_', '') + '/' + 
            df['name']
        ),
        'data_columns': COMMON_COLUMNS + ['resource_type', 'raw_code'], # 'config', 'depends_on'
    },
    'schema': {
        'path': lambda df: df['path'],
        'data_columns': ['name', 'tables'],
    },    
    'exposure': {
        'path': lambda df: '',
        'data_columns': ['name', 'owner', 'type', 'description', 'url', 'depends_on'],
    },
}


if not os.path.isfile(MANIFEST_FILE):
    urllib.request.urlretrieve('https://dbt.gitlabdata.com/manifest.json', MANIFEST_FILE)

if not os.path.isfile(CATALOG_FILE):
    urllib.request.urlretrieve('https://dbt.gitlabdata.com/catalog.json', CATALOG_FILE)



MANIFEST = json.load(open(MANIFEST_FILE, encoding='utf-8'))
CATALOG = json.load(open(CATALOG_FILE, encoding='utf-8'))


def stringify_bytes(bytes):
    if bytes < 0:
        return ''
    if bytes > pow(2, 40):
        return f'{bytes / pow(2, 40):,.1f} TB'
    if bytes > pow(2, 30):
        return f'{bytes / pow(2, 30):,.1f} GB'
    if bytes > pow(2, 20):
        return f'{bytes / pow(2, 20):,.1f} MB'
    if bytes > pow(2, 10):
        return f'{bytes / pow(2, 10):,.1f} kB'
    return f'{bytes} B'
    

def get_dataframe(key):
    if key == 'exposures':
        df = pd.DataFrame(MANIFEST[key].values())
        df = df.sort_values(['type', 'name'])
        df['description'] = df['description'].map(lambda desc: desc.replace('\n', ' '))
    else:
        df_from_manifest = pd.DataFrame(MANIFEST[key].values())
        df_from_catalog = pd.DataFrame(CATALOG[key].values())
        df_from_manifest = df_from_manifest[[c for c in df_from_manifest.columns if c != 'columns']]
        df = df_from_manifest.merge(df_from_catalog, on='unique_id')
        df['type'] = df['metadata'].map(lambda metadata: metadata['type'])
        df['owner'] = df['metadata'].map(lambda metadata: metadata['owner'])
        df['size'] = df['stats'].map(lambda stats: stringify_bytes(stats.get('bytes', {}).get('value', -1)))
        df['last_modified'] = df['stats'].map(lambda stats: stats.get('last_modified', {}).get('value'))
        df['columns'] = df['columns'].map(dict.values).map(list)
    # if 'depends_on' in df.columns:
    #     df['depends_on'] = df['depends_on'].map(lambda dep: dep['nodes'])
    df = df.fillna('')
    return df


def format_df(df, asset_type):
    conf = ASSET_TYPES[asset_type]
    df['asset_type'] = asset_type
    df['path'] = conf['path'](df)
    df['data'] = df[conf['data_columns']].to_dict(orient='records')
    return df[['asset_type', 'path', 'data']]


def get_schemas_from_nodes(nodes):
    schemas = nodes.copy()
    schemas['path'] = schemas['path'].map(lambda path: '/'.join(path.split('/')[:-1]) + '/index')
    schemas['name'] = schemas['path'].map(lambda path: path.split('/')[1])
    schemas['table'] = schemas['data'].map(lambda data: data['name'])
    schemas = schemas.groupby('path').agg(
        name=('name', 'max'),
        tables=('table', list),
    ).reset_index()
    return schemas

sources = get_dataframe('sources')
nodes = get_dataframe('nodes')



raw_data_schemas = sorted(pd.concat([
    sources['schema'],
    nodes.loc[nodes['database'] == 'RAW']['schema'],
]).unique())
raw_data = pd.DataFrame({
    'asset_type': ['raw_data'],
    'path': ['Raw Data/index'],
    'data': [{'schemas': raw_data_schemas}],
})

source_models_schemas = sorted(nodes.loc[nodes['database'] == 'PREP']['schema'].unique())
source_models = pd.DataFrame({
    'asset_type': ['source_models'],
    'path': ['Source Models/index'],
    'data': [{'schemas': source_models_schemas}],
})


sources = format_df(sources, 'source')
nodes = format_df(nodes, 'node')
schemas = get_schemas_from_nodes(pd.concat([sources, nodes]))
schemas = format_df(schemas, 'schema')

# snapshots = nodes.loc[nodes['resource_type'] == 'snapshot']
# models = nodes.loc[nodes['resource_type'] == 'model']
# prep_models = models.loc[nodes['database'] == 'PREP']
# prod_models = models.loc[nodes['database'] != 'PROD']
# raw_models = models.loc['']


exposures = get_dataframe('exposures')
exposures = format_df(exposures, 'exposure')
exposures = pd.DataFrame({
    'asset_type': ['exposures'],
    'path': ['exposures/index'],
    'data': [{'exposures': exposures['data'].to_list()}],
})    


home = pd.DataFrame({
    'asset_type': ['homepage'],
    'path': ['index'],
    'data': [{}],
})


# nodes = get_dataframe('nodes')
# snapshots = nodes.loc[nodes['resource_type'] == 'snapshot']
# seeds = nodes.loc[nodes['resource_type'] == 'seed']
# prep_models = nodes.loc[(nodes['resource_type'] == 'model') & (nodes['database'] == 'PREP')]
# prod_models = nodes.loc[(nodes['resource_type'] == 'model') & (nodes['database'] != 'PREP')]
# breakpoint()

# config
# depends_on
# tags
assets = pd.concat([home, raw_data, source_models, schemas, exposures, sources, nodes])
assets.to_parquet(f'{HERE}/assets.parquet')


# sources['created_at'] = sources['created_at'].map(lambda ts: datetime.datetime.utcfromtimestamp(1347517370).strftime('%Y-%m-%d %H:%M:%S'))
# sources['row_count'] = sources['stats'].map(lambda stats: stats.get('row_count', {}).get('value', 10))
