import argparse
import json
import os
import urllib.request

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')


def merge_columns(manifest_columns, catalog_columns):
    if isinstance(catalog_columns, dict) and catalog_columns:
        return [
            {
                'name': name,
                'type': col['type'] or '',
                'description': col['comment'] or manifest_columns.get(name, {}).get('description')
            }
            for name, col in catalog_columns.items()
        ]
    elif isinstance(manifest_columns, dict):
        return [
            {
                'name': name,
                'type': col['data_type'] or '',
                'description': col['description'] or ''
            }
            for name, col in manifest_columns.items()
        ]
    return []


parser = argparse.ArgumentParser()
parser.add_argument('manifest_file')
parser.add_argument('catalog_file')
args = parser.parse_args()

manifest_file = args.manifest_file
catalog_file = args.catalog_file

manifest = json.load(open(manifest_file, encoding='utf-8'))
catalog = json.load(open(catalog_file, encoding='utf-8'))

nodes_from_manifest = pd.DataFrame(manifest['nodes'].values())
nodes_from_catalog = pd.DataFrame(catalog['nodes'].values())

nodes = nodes_from_manifest.merge(nodes_from_catalog, on='unique_id', how='left', suffixes=['_manifest', '_catalog'])

nodes['path'] = nodes['path'].map(lambda path: path.replace('\\', '/'))
nodes['folder'] = nodes['path'].map(lambda path: '/'.join(path.split('/')[:-1]))
nodes['columns'] = [
    merge_columns(manifest_columns, catalog_columns)
    for manifest_columns, catalog_columns in zip(nodes['columns_manifest'], nodes['columns_catalog'])
]
del nodes['columns_manifest']
del nodes['columns_catalog']

models = nodes.loc[nodes['resource_type'] == 'model']

# remove models in root folder
models = models.loc[models['folder'] != '']

assets = pd.DataFrame({
    'path': models['path'],
    'asset_type': 'model',
    'data': models.to_dict(orient='records'),
})

# TO REMOVE AFTERWARD: WE KEPT THIS TO ACCELERATE TESTING
# assets = assets.sort_values('path').iloc[:100]

assets.to_json(f'{HERE}/assets.jsonl', orient='records', lines=True)
