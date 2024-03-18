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
        'path': lambda df: 'raw_data/' + df['schema'] + '/' + df['name'],
        'data_columns': COMMON_COLUMNS + ['loader'],
    },
    'node': {
        'path': lambda df: get_node_path(df),
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


def get_node_path(df):
    paths = []
    models_tree = {}
    for node in df.to_dict(orient='records'):
        schema = node['schema']
        if schema.startswith('restricted_safe_'):
            schema = schema[len('restricted_safe_'):]
        schema_prefix, schema_suffix = schema.split('_', 1) if '_' in schema else (schema, '')
        if schema_prefix == 'workspace':
            paths.append('team_workspaces/' + schema_suffix + '/' + node['name'])
        elif node['database'] == 'RAW':
            paths.append(f"raw_data/{schema}/{node['name']}")
        elif node['database'] == 'PREP':
            paths.append(f"source_models/{schema}/{node['name']}")
        elif schema.lower() == 'legacy':
            paths.append(f"legacy/{schema}/{node['name']}")
        elif node['name'].startswith(('prep_', 'fct_', 'dim_', 'mart_', 'rpt_', 'pump_', 'map_', 'bdg_')):
            paths.append(f"models/{schema}/{node['name']}")
            _dict = models_tree
            for part in node['name'].split('_')[1:]:
                _dict[part] = _dict.get(part, {}) 
                _dict = _dict[part]
            _dict['item'] = {}
        else:
            paths.append(f"legacy/{schema}/{node['name']}")

    iterate = True
    while iterate:
        iterate = False
        models_tree_keys = list(models_tree.keys())
        nb_keys = len(models_tree_keys)
        for key in models_tree_keys:
            subkeys = list(models_tree[key].keys())
            if len(subkeys) == 1:
                subkey = subkeys[0]
                if subkey == 'item':
                    continue
                models_tree[key + '_' + subkey] = models_tree[key][subkey]
                del models_tree[key]
                iterate = True
    models_folders = models_tree.keys()

    paths_with_subfolders = []
    for path in paths:
        if path.startswith('models/'):
            _, schema, name = path.split('/')
            prefix, suffix = name.split('_', 1)
            folder = next(f for f in models_folders if suffix.startswith(f))
            path = f'models/{schema}/{folder}/{prefix}_{suffix}'
        paths_with_subfolders.append(path)
    return paths_with_subfolders
    

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


sources = get_dataframe('sources')
nodes = get_dataframe('nodes')


sources = format_df(sources, 'source')
nodes = format_df(nodes, 'node')

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

assets = pd.concat([home, exposures, sources, nodes])
assets.to_parquet(f'{HERE}/assets.parquet')



# snapshots = nodes.loc[nodes['resource_type'] == 'snapshot']
# seeds = nodes.loc[nodes['resource_type'] == 'seed']
# config
# depends_on
# tags
# sources['created_at'] = sources['created_at'].map(lambda ts: datetime.datetime.utcfromtimestamp(1347517370).strftime('%Y-%m-%d %H:%M:%S'))
# sources['row_count'] = sources['stats'].map(lambda stats: stats.get('row_count', {}).get('value', 10))


