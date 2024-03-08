![logo](https://github.com/unytics/catalog_builder/assets/111615732/bdb75e70-c7cd-4c7b-aa28-f015011f1edb)



<p align="center">
    <em>Build a custom data-catalog in minutes</em>
</p>

---

<br>

## 🔍️ 1. What is CatalogBuilder?

- CatalogBuilder is a simple tool to **generate & deploy a documentation website for your data assets**.
- It enables anyone at your company to **quickly find the trusted data they are looking for**. 

<br>

## 💡  2. Why CatalogBuilder?

> There are **many open-source projects** (*admundsen, open-metadata, datahub, metacat, atlas*) to build such a catalog in-house. But as they offer a lot of advanced features, they are **hard to manage and deploy** if you're not a tech expert. They can be even **harder to customize**. 
> 
> **dbt docs** is great to generate a documentation website on top of your dbt assets but:
> 
> - it focuses on dbt only (while you are interested in other sources + metadata)
> - is very hard to customize (except you're an angular expert)
> - can be slow.

<br>

👉 CatalogBuilder aims at offering a **lightweight alternative** to generate a documentation website on top of your data assets. It focuses on **read-only data discovery** and:

1. ✔️ can be easily customized and deployed by low tech people
2. ✔️ can then handle the very specific needs of your company
3. ✔️ is fast and lightweight
4. ✔️ is built on top of the very famous [mkdocs-material](https://github.com/squidfunk/mkdocs-material) python library which is used by millions of developers to deploy their documentation (*such as [fastapi](https://fastapi.tiangolo.com/)*).


<br>

## 💥 3. Getting Started with `catalog` CLI

> `catalog` is the CLI (command-line-interface) of CatalogBuilder to generate, show & deploy the documentation.

### 3.1 Install `catalog` 🛠️

``` sh
pip install catalog-builder
```

### 3.2 Create your first documentation configuration 👨‍💻

To get started, let's download a catalog configuration example and play with it. The following command will download the [`catalogs/bigquery_public_data`](https://github.com/unytics/catalog_builder/tree/main/catalogs/bigquery_public_data) folder on your laptop.

``` sh
catalog download bigquery_public_data
```

> You will find the following files in the folder:
> 
> - `assets file`: a file containing the list of the assets you want to put in your documentation. It can be a parquet file named `assets.parquet` or a [json lines file](https://medium.com/@sujathamudadla1213/difference-between-ordinary-json-and-json-lines-fc746f93d75e) named  `assets.jsonl`. Each asset in the file must have the following fields:
>   - `asset_type`: for example: `table`.
>   - `documentation_path`: the path of the asset page in the generated documentation. For example `dataset_name/table_name`.
>   - `data`: a dict of the attributes of the asset needed to generate the documentation. For example `{"name": "foo"}`
> - `generate_assets_file.py`: the python script used to (re)generate the `assets file`.
> - `requirements.txt`: the python requirements needed by `generate_assets_file.py`.
> - `templates`: a folder which includes a jinja-template markdown-file for every `asset_type`. These templates are used to generate a markdown documentation file for each asset.
> - `mkdocs.yml`: the mkdocs configuration file used by mkdocs to build the documentation website from the generated markdown files.


### 3.3 Build and Show the documentation website locally! ⚡

``` sh
catalog serve bigquery_public_data
```

You can now see the generated documentation at http://localhost:8000.

> 1. For each asset of the `assets file`, the jinja template of `asset_type` will be rendered using the asset `data` to generate a markdown file which will be written into `catalogs/bigquery_public_data/docs/` at `documentation_path`.
> 2. Mkdocs will then build the documentation website from the markdown files into `catalogs/bigquery_public_data/site` (using `mkdocs.yml` configuration file).
> 3. Mkdocs will serve the site at http://localhost:8000.


### 3.4 Deploy the documentation website! 🚀

**A. To deploy on GitHub pages**:

``` sh
catalog gh-deploy bigquery_public_data
```

> 1. For each asset of the `assets file`, the jinja template of `asset_type` will be rendered using the asset `data` to generate a markdown file which will be written into `catalogs/bigquery_public_data/docs/` at `documentation_path`.
> 2. Mkdocs will then build the documentation website from the markdown files into `catalogs/bigquery_public_data/site` (using `mkdocs.yml` configuration file).
> 3. Mkdocs will [deploy the site on GitHub pages](https://www.mkdocs.org/user-guide/deploying-your-docs/) (this only works if you are on a github repository).


**B. To deploy elsewhere**:

You can follow [these instructions](https://www.mkdocs.org/user-guide/deploying-your-docs/#other-providers) from mkdocs.

<br>


## 💎 4. Generate dbt documentation

1. Change directory to your dbt project directory
3. Download `catalogs/dbt` documentation example by running `catalog download dbt`.
2. Run `dbt docs generate` to compute `target/manifest.json` and `target/catalog.json`.
4. Generate the assets file by running `python catalogs/dbt/generate_assets_file.py`. The script will parse `target/manifest.json` and `target/catalog.json` to generate the `assets file` in the expected format.
5. Run `catalog serve dbt` to build the website and show it locally.


