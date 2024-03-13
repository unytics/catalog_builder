import json
import os
import urllib.request
import datetime

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))

MANIFEST_FILE = f'{HERE}/tmp_manifest.json'
CATALOG_FILE = f'{HERE}/tmp_catalog.json'

ASSET_TYPES = {
    'source': {
        'path': lambda df: 'sources/' + df['schema'] + '/' + df['name'],
        'data_columns': ['database', 'schema', 'name', 'type', 'loader', 'description', 'created_at', 'owner', 'size', 'last_modified', 'columns'],
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



def get_schemas_from_sources(sources):
    schemas = sources.copy()
    schemas['path'] = 'sources/' + schemas['schema'] + '/index'
    schemas = schemas.groupby('path').agg(
        name=('schema', 'max'),
        description=('source_description', 'max'),
        tables=('name', list),
    ).reset_index()
    schemas['asset_type'] = 'schema'
    schemas['data'] = schemas[['name', 'description', 'tables']].to_dict(orient='records')
    return schemas[['asset_type', 'path', 'data']]


sources = get_dataframe('sources')
schemas = get_schemas_from_sources(sources)
sources = format_df(sources, 'source')
source_homepage = pd.DataFrame({
    'asset_type': ['source_homepage'],
    'path': ['sources/index'],
    'data': [{'schemas': schemas['data'].map(lambda data: data['name']).to_list()}],
})

nodes = get_dataframe('nodes')

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
assets = pd.concat([home, exposures, schemas, sources, source_homepage])
assets.to_parquet(f'{HERE}/assets.parquet')


# sources['created_at'] = sources['created_at'].map(lambda ts: datetime.datetime.utcfromtimestamp(1347517370).strftime('%Y-%m-%d %H:%M:%S'))
# sources['row_count'] = sources['stats'].map(lambda stats: stats.get('row_count', {}).get('value', 10))
# sources = list(MANIFEST['sources'].values())
# nodes = list(MANIFEST['nodes'].values())
# models = [n for n in nodes if n['resource_type'] in ['model', 'seed', 'snapshot']]




