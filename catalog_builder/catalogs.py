import shutil
import os

import jinja2
import pandas as pd

CATALOGS_CONF_FOLDER = 'catalogs'

class CatalogException(Exception):
    pass


class Catalog:

    def __init__(self, name):
        self.name = name
        self.folder = f'{CATALOGS_CONF_FOLDER}/{name}'
        self.load_templates()
        self._assets = None

    def load_templates(self):
        template_folder = f'{self.folder}/templates'
        self.templates = {}
        if not os.path.isdir(template_folder):
            os.makedirs(template_folder)
            return
        for f in os.listdir(template_folder):
            template = open(f'{template_folder}/{f}', encoding='utf-8').read()
            template = jinja2.Template(template)
            asset_type =  f.replace('.md', '')
            self.templates[asset_type] = template

    @property
    def assets(self):
        if self._assets is not None:
            return self._assets
        if os.path.isfile(f'{self.folder}/assets.parquet'):
            self._assets = pd.read_parquet(f'{self.folder}/assets.parquet')
        elif os.path.isfile(f'{self.folder} /assets.jsonl'):
            self._assets = pd.read_json(f'{self.folder}/assets.jsonl', lines=True)
        else:
            raise CatalogException(f'Could not find any assets file. Neither `{self.folder}/assets.parquet` nor `{self.folder}/assets.jsonl` exist. Please generate them.')
        return self._assets

    def generate_markdown(self):
        shutil.rmtree(f'{self.folder}/docs', ignore_errors=True)
        for k, asset in enumerate(self.assets.to_dict(orient='records')):
            if not asset['path'] or asset['asset_type'] not in self.templates:
                continue
            template = self.templates[asset['asset_type']]
            content = template.render(**asset['data'])
            path = asset['path'].replace('\\', '/')
            path = f'{self.folder}/docs/{path}'
            if not path.endswith('.md'):
                path += '.md'
            folder = '/'.join(path.split('/')[:-1])
            os.makedirs(folder, exist_ok=True)
            with open(path, 'w', encoding='utf8') as out:
                out.write(content)
            # if k > 1000:
            #     break
        if os.path.isfile(f'{self.folder}/style.css'):
            shutil.copyfile(f'{self.folder}/style.css', f'{self.folder}/docs/style.css')
