import json
import os
import urllib.request
import datetime

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))

MANIFEST_FILE = f'{HERE}/tmp_manifest.json'
CATALOG_FILE = f'{HERE}/tmp_catalog.json'


if not os.path.isfile(MANIFEST_FILE):
    urllib.request.urlretrieve('https://dbt.gitlabdata.com/manifest.json', MANIFEST_FILE)

if not os.path.isfile(CATALOG_FILE):
    urllib.request.urlretrieve('https://dbt.gitlabdata.com/catalog.json', CATALOG_FILE)


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
    

manifest = json.load(open(MANIFEST_FILE, encoding='utf-8'))
catalog = json.load(open(CATALOG_FILE, encoding='utf-8'))


def get_sources():
    sources_from_manifest = pd.DataFrame(manifest['sources'].values())
    sources_from_catalog = pd.DataFrame(catalog['sources'].values())
    sources_from_manifest = sources_from_manifest[[c for c in sources_from_manifest.columns if c != 'columns']]
    return sources_from_manifest.merge(sources_from_catalog, on='unique_id')


def get_models():
    models_from_manifest = pd.DataFrame(manifest['nodes'].values())
    models_from_catalog = pd.DataFrame(catalog['nodes'].values())
    models_from_manifest = models_from_manifest[[c for c in models_from_manifest.columns if c != 'columns']]
    models_from_manifest = models_from_manifest.loc[models_from_manifest['resource_type'].isin(['model', 'seed', 'snapshot'])]
    return models_from_manifest.merge(models_from_catalog, on='unique_id')


def get_schemas_from_sources(sources):
    schemas = sources.copy()
    schemas['path'] = schemas['database'] + '/' + schemas['schema'] + '/index'
    schemas = schemas.groupby('path').agg(
        name=('schema', 'max'),
        description=('source_description', 'max'),
        tables=('name', list),
    ).reset_index()
    schemas['asset_type'] = 'schema'
    schemas['data'] = schemas[['name', 'description', 'tables']].to_dict(orient='records')
    return schemas[['asset_type', 'path', 'data']]


def get_databases_from_sources(sources):
    databases = sources.copy()
    databases['path'] = databases['database'] + '/index'
    databases = databases.groupby('path').agg(
        name=('database', 'max'),
        schemas=('schema', lambda x: sorted(list(set(x)))),
    ).reset_index()
    databases['asset_type'] = 'database'
    databases['data'] = databases[['name', 'schemas']].to_dict(orient='records')
    return databases[['asset_type', 'path', 'data']]


def transform_sources(sources):
    sources['asset_type'] = 'source'
    sources['path'] = sources['database'] + '/' + sources['schema'] + '/' + sources['name']
    sources['type'] = sources['metadata'].map(lambda metadata: metadata['type'])
    sources['owner'] = sources['metadata'].map(lambda metadata: metadata['owner'])
    sources['size'] = sources['stats'].map(lambda stats: stringify_bytes(stats.get('bytes', {}).get('value', -1)))
    sources['last_modified'] = sources['stats'].map(lambda stats: stats.get('last_modified', {}).get('value'))
    sources['columns'] = sources['columns'].map(dict.values).map(list)
    sources = sources.fillna('')
    sources['data'] = sources[['database', 'schema', 'name', 'type', 'loader', 'description', 'created_at', 'owner', 'size', 'last_modified', 'columns']].to_dict(orient='records')
    sources = sources[['asset_type', 'path', 'data']].fillna('')
    return sources


sources = get_sources()
databases = get_databases_from_sources(sources)
schemas = get_schemas_from_sources(sources)
sources = transform_sources(sources)
source_homepage = pd.DataFrame({
    'asset_type': ['source_homepage'],
    'path': ['index'],
    'data': [{'databases': databases['data'].map(lambda data: data['name']).to_list()}],
})


# models = get_models()
# breakpoint()

assets = pd.concat([databases, schemas, sources, source_homepage])
assets.to_parquet(f'{HERE}/assets.parquet')


# sources['created_at'] = sources['created_at'].map(lambda ts: datetime.datetime.utcfromtimestamp(1347517370).strftime('%Y-%m-%d %H:%M:%S'))
# sources['row_count'] = sources['stats'].map(lambda stats: stats.get('row_count', {}).get('value', 10))
# sources = list(manifest['sources'].values())
# nodes = list(manifest['nodes'].values())
# models = [n for n in nodes if n['resource_type'] in ['model', 'seed', 'snapshot']]

# sources = pd.DataFrame(sources)
# models = pd.DataFrame(models)



