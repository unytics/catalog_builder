# Create a catalog from dbt models

This example will generate a static documentation website of dbt models.

It is an improvement over the original dbt docs for business people as:

- only models are shown in the documentation (and not sources, etc). That reduce visual noise.
- `README.md` files located in models folder and subfolders will be rendered on the website. It becomes super-easy to document categories of models.

We deployed this example for the dbt project of Gitlab Data Team [here](http://catalogs.unytics.io/dbt/).

The rest of the document presents how to build and serve the documentation.


## Generate dbt artefacts files

We will use dbt artifact files as input for creating `assets.jsonl` file and then for generating the website.

Create these artefacts files by running from your dbt folder:

```
dbt docs generate
```

This will generate two files: `manifest.json` and `catalog.json` in `target` folder.

> If you haven't any dbt project but still want to try this example, you can download the public files of Gitlab Data team. Here are the links:
>
> - [manifest.json](https://dbt.gitlabdata.com/manifest.json)
> - [catalog.json](https://dbt.gitlabdata.com/catalog.json)



## Install Catalog-Builder

```
pip install catalog-builder
```

## Download this example

```
catalog download dbt_1.8__models_only
```

This folder will be downloaded into `catalogs/dbt_1.8__models_only`


## Generate Assets File

Generate `assets.jsonl` with:

```
python catalogs/dbt_1.8__models_only/generate_assets_file.py "path/to/manifest.json" "path/to/catalog.json"
```


## Build the website

Specify the path to your dbt models folder so that the catalog builder uses the README files included in it (recursively).

```
catalog build dbt_1.8__models_only --markdown_folder_paths_to_include path/to/your/dbt/models --add_children_in_folder_pages
```


If you are using the dbt artifact files of Gitlab Data team (as seen above), we created some README in `models_gitlab_team` folder. You can then run:

```
catalog build dbt_1.8__models_only --markdown_folder_paths_to_include catalogs/dbt_1.8__models_only/models_gitlab_team --add_children_in_folder_pages
```

> To change the website name and logos, you can update mkdocs.yml


## Launch the website locally

```
catalog serve dbt_1.8__models_only
```


## Deploy the website

On Cloud Storage:

```
catalog deploy gcs dbt_1.8__models_only
```

> The files will be uploaded in a bucket as defined by the `site_url` field in mkdocs.yml.
> If the `site_url` is `https://catalogs.unytics.io/dbt/` then the files will be copied into `catalogs.unytics.io` cloud storage bucket to `gs://catalogs.unytics.io/dbt/`