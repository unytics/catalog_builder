![logo](https://github.com/unytics/catalog_builder/assets/111615732/bdb75e70-c7cd-4c7b-aa28-f015011f1edb)



<p align="center">
    <em>Build a custom data-catalog in minutes</em>
</p>

---

<br>

## 🔍️ What is CatalogBuilder?

- CatalogBuilder is a simple tool to **generate & deploy a documentation website** on top of your **data assets**.
- It enables anyone at your company to **quickly find the trusted data they are looking for**. 

<br>

## 💡  Why CatalogBuilder?

> There are **many open-source projects** (*admundsen, open-metadata, datahub, metacat, atlas*) to build such a catalog in-house. But as they offer a lot of advanced features, they are **hard to manage and deploy** if you're not a tech expert. They can be even **harder to customize**. 
> 
> **dbt docs** is great to generate a documentation website on top of your dbt assets but:
> 
> - it focuses on dbt only (while you are interested in other sources + metadata)
> - is very hard to customize (except you're an angular expert)
> - can be slow.

<br>

👉 CatalogBuilder aims at offering a **lightweight alternative** to generate a documentation website on top of your data assets. It focuses on **read-only data discovery** and:

- ✔️ can be easily customized and deployed by low tech people
- ✔️ can then handle the very specific needs of your company
- ✔️ is fast and lightweight
- ✔️ is built on top of the very famous [mkdocs-material](https://github.com/squidfunk/mkdocs-material) python library which is used by millions of developers to deploy their documentation (*such as [fastapi](https://fastapi.tiangolo.com/)*).


<br>

## 💥 Getting Started with `cb` CLI

> `cb` is the CLI (command-line-interface) of CatalogBuilder to generate, show & deploy the documentation.

### Install `cb` 🛠️

``` sh
pip install catalog-builder
```

### Create your first documentation configuration 👨‍💻

``` sh
cb get-example simple
```

> This will download the `catalogs/simple` folder from this repository. You will find the following files in the folder:
> 
> - `assets.jsonl`: a [json lines file](https://medium.com/@sujathamudadla1213/difference-between-ordinary-json-and-json-lines-fc746f93d75e) which contains all the assets you want to put in your documentation. Each asset must have at least the following field:
>   - `asset_type`: for example: `table`.
>   - `documentation_path`: the path of the asset page in the generated documentation.
>   - `data`: a json of the attributes of the asset needed to generate the documentation.
> - `templates`: afolder which includes a jinja template markdown file for every `asset_type`. These templates are used to generate a markdown documentation file for each asset.
> - `mkdocs.yml`: the mkdocs configuration file used by mkdocs to build the documentation website from the generated markdown files.


### Build and show the documentation website locally! ⚡

``` sh
cb serve simple
```

You can now see the generated documentation at http://localhost:8000.

> - For each asset of `assets.jsonl`, the jinja template of `asset_type` will be rendered using the asset `data` to generate a markdown file which will be written into `catalogs/simple/generated_markdown` at `documentation_path`.
> - Mkdocs will then build the documentation website from the markdown files and using `mkdocs.yml` configuration file and serve it at http://localhost:8000.


