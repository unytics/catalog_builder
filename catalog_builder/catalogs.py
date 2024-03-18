import shutil
import os

import jinja2
import pandas as pd

from .utils import CatalogException


CATALOGS_CONF_FOLDER = 'catalogs'


FOLDER_TEMPLATE = jinja2.Template('''# {{ name }}

<div class="grid cards" markdown>

-   {% for obj in files_and_folders -%}
    {% if obj.type == 'file' -%}
    :material-file: [{{ obj.name | replace('.md', '') }}]({{ obj.name }})<br>
    {% else -%}
    :material-folder: [{{ obj.name }}]({{ obj.name }}/index.md)<br>
    {% endif %}
    {% endfor %}

</div>
''')



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
            raise CatalogException(f'Could not find any assets file. Neither `{self.folder}/assets.parquet` nor `{self.folder}/assets.jsonl` exist. Please generate the file by running `{self.folder}/generate_assets_file.py`.')
        return self._assets

    def generate_markdown(self):
        shutil.rmtree(f'{self.folder}/docs', ignore_errors=True)
        self._generate_markdown_of_assets()
        self._generate_markdown_of_folders()
        if os.path.isfile(f'{self.folder}/style.css'):
            shutil.copyfile(f'{self.folder}/style.css', f'{self.folder}/docs/style.css')

    def _generate_markdown_of_assets(self):
        for asset in self.assets.to_dict(orient='records'):
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

    def _generate_markdown_of_folders(self):
        for root, folders, files in os.walk(f'{self.folder}/docs/'):
            if 'index.md' in files:
                continue
            root_name = os.path.basename(root)
            files = [{'name': f, 'type': 'file'} for f in files]
            folders = [{'name': f, 'type': 'folder'} for f in folders]
            files_and_folders = sorted(files + folders, key=lambda x: x['name'])
            content = FOLDER_TEMPLATE.render(
                files_and_folders=files_and_folders,
                name=root_name,
            )
            open(f'{root}/index.md', 'w', encoding='utf-8').write(content)
