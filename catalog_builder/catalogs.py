import os
import shutil

import jinja2
import pandas as pd

from .utils import CatalogException

CATALOGS_CONF_FOLDER = "catalogs"


FOLDER_TEMPLATE = jinja2.Template(
    """---
search:
  exclude: true
---

{{ content }}

{% if files_and_folders %}

<div class="grid cards" markdown>

-   {% for obj in files_and_folders -%}
    {% if obj.type == 'file' -%}
    :material-file: [{{ obj.name | replace('.md', '') }}]({{ obj.name }})<br>
    {% else -%}
    :material-folder: [{{ obj.name }}]({{ obj.name }}/index.md)<br>
    {% endif %}
    {% endfor %}

</div>

{% endif %}
"""
)


class Catalog:

    def __init__(self, name):
        self.name = name
        self.folder = f"{CATALOGS_CONF_FOLDER}/{name}"
        self.generated_docs_folder = f"{self.folder}/docs"
        self.load_templates()
        self._assets = None

    def load_templates(self):
        template_folder = f"{self.folder}/templates"
        self.templates = {}
        if not os.path.isdir(template_folder):
            os.makedirs(template_folder)
            return
        for root, folders, files in os.walk(template_folder):
            for file in files:
                template = open(f"{root}/{file}", encoding="utf-8").read()
                template = jinja2.Template(template)
                filename = f"{root}/{file}".replace(template_folder + "/", "")
                asset_type = filename.replace(".md", "")
                self.templates[asset_type] = template

    @property
    def assets(self):
        if self._assets is not None:
            return self._assets
        if os.path.isfile(f"{self.folder}/assets.parquet"):
            self._assets = pd.read_parquet(f"{self.folder}/assets.parquet")
        elif os.path.isfile(f"{self.folder} /assets.jsonl"):
            self._assets = pd.read_json(f"{self.folder}/assets.jsonl", lines=True)
        else:
            raise CatalogException(
                f"Could not find any assets file. Neither `{self.folder}/assets.parquet` nor `{self.folder}/assets.jsonl` exist. Please generate the file by running `{self.folder}/generate_assets_file.py`."
            )
        return self._assets

    def generate_markdown(self, markdown_folder_paths_to_include=None, add_children_in_folder_pages=False):
        shutil.rmtree(self.generated_docs_folder, ignore_errors=True)
        self._copy_files_from_markdown_folders(markdown_folder_paths_to_include)
        self._generate_markdown_of_assets()
        if add_children_in_folder_pages:
            self._generate_markdown_of_folders()

    def _copy_files_from_markdown_folders(self, markdown_folder_paths_to_include):
        if not markdown_folder_paths_to_include:
            return
        assert isinstance(markdown_folder_paths_to_include, list), 'markdown_folder_paths_to_include must be a list'

        def files_to_ignore(path, names):
            return [
                name
                for name in names
                if '.' in name and not name.endswith(('.md', '.css', '.js', '.html', '.png', '.jpg', '.jpeg'))
            ]

        for folder in markdown_folder_paths_to_include:
            if os.path.isdir(folder):
                shutil.copytree(folder, self.generated_docs_folder, dirs_exist_ok=True, ignore=files_to_ignore)

    def _generate_markdown_of_assets(self):
        for asset in self.assets.to_dict(orient="records"):
            if not asset["path"] or asset["asset_type"] not in self.templates:
                continue
            template = self.templates[asset["asset_type"]]
            content = template.render(**asset["data"])
            path = asset["path"].replace("\\", "/")
            path = f"{self.generated_docs_folder}/{path}"
            if not path.endswith(".md"):
                path += ".md"
            folder = "/".join(path.split("/")[:-1])
            os.makedirs(folder, exist_ok=True)
            with open(path, "w", encoding="utf8") as out:
                out.write(content)

    def _generate_markdown_of_folders(self):
        for root, folders, files in os.walk(self.generated_docs_folder):
            index_file = next((file for file in files if file.lower() in ['index.md', 'readme.md']), None)
            if index_file in files:
                content = open(f"{root}/{index_file}", encoding="utf-8").read()
            else:
                content = "# " + os.path.basename(root).replace("_", " ").title()
            if root == self.generated_docs_folder:
                files_and_folders = None
            else:
                files = [{"name": f, "type": "file"} for f in files if f != "index.md"]
                folders = [{"name": f, "type": "folder"} for f in folders]
                files_and_folders = sorted(files + folders, key=lambda x: x["name"])
            content = FOLDER_TEMPLATE.render(
                files_and_folders=files_and_folders,
                content=content,
            )
            index_file = index_file or 'index.md'
            open(f"{root}/{index_file}", "w", encoding="utf-8").write(content)
