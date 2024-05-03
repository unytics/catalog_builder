import os

import click
from click_help_colors import HelpColorsGroup

from .catalogs import Catalog
from .utils import (
    CatalogException,
    download_github_folder,
    exec,
    handle_error,
    load_yaml_file,
    print_info,
    print_success,
)


@click.group(
    cls=HelpColorsGroup, help_headers_color="yellow", help_options_color="cyan"
)
def cli():
    pass


@cli.command()
@click.argument("catalog_name")
@handle_error
def download(catalog_name):
    """
    Download CATALOG_NAME configuration folder from `catalog_builder` GitHub
    """
    if os.path.isdir(f"catalogs/{catalog_name}"):
        raise CatalogException(
            f"`catalogs/{catalog_name}` folder already exists. If you wish to download it again please remove the folder beforehand."
        )
    download_github_folder(f"catalogs/{catalog_name}")
    print_success(f"Downloaded `catalogs/{catalog_name}`")


@cli.command()
@click.argument("catalog_name")
@click.option("--markdown_only", is_flag=True)
@click.option("--markdown_folder_paths_to_include", default="catalogs/<catalog_name>/source_docs")
@click.option("--add_children_in_folder_pages", is_flag=True)
@handle_error
def build(catalog_name, markdown_only, markdown_folder_paths_to_include, add_children_in_folder_pages):
    """
    Build CATALOG_NAME catalog (builds docs/ and site/)
    """
    catalog = Catalog(catalog_name)
    print_info(f"Generating mardown files into {catalog.folder}/docs")
    markdown_folder_paths_to_include = markdown_folder_paths_to_include.replace('<catalog_name>', catalog_name).split(',')
    catalog.generate_markdown(
        markdown_folder_paths_to_include=markdown_folder_paths_to_include,
        add_children_in_folder_pages=add_children_in_folder_pages, 
    )
    if markdown_only:
        return
    config_file = f"catalogs/{catalog_name}/mkdocs.yml"
    if not os.path.isfile(config_file):
        raise CatalogException(f"Missing config file {config_file}")
    print_info(f"Building site from mardown files into {catalog.folder}/site")
    exec(f"mkdocs build --config-file {config_file}")


@cli.command()
@click.argument("catalog_name")
@click.option(
    "--port",
    default=8000,
    help="port on which the catalog will be exposed",
    show_default=True,
)
@handle_error
def serve(catalog_name, port):
    """
    Serve CATALOG_NAME by default website on http://localhost:8000
    """
    catalog = Catalog(catalog_name)
    if not os.path.isdir(f"{catalog.folder}/site"):
        raise CatalogException(
            f"`{catalog.folder}/site` folder does not exist. Please build it with `build` command"
        )
    print_info(
        f"Serving website. Open this url in your browser --> http://localhost:{port} !"
    )
    exec(f"python -m http.server {port} --directory {catalog.folder}/site")


@cli.command()
@click.argument("catalog_name")
@click.option("--markdown_folder_paths_to_include", default="catalogs/<catalog_name>/source_docs")
@click.option("--add_children_in_folder_pages", is_flag=True)
@click.option(
    "--port",
    default=8000,
    help="port on which the catalog will be exposed",
    show_default=True,
)
@handle_error
def build_and_serve(catalog_name, markdown_folder_paths_to_include, add_children_in_folder_pages, port):
    """
    Serve CATALOG_NAME website on http://localhost:8000
    """
    catalog = Catalog(catalog_name)
    print_info(f"Generating mardown files into {catalog.folder}/docs")
    markdown_folder_paths_to_include = markdown_folder_paths_to_include.replace('<catalog_name>', catalog_name).split(',')
    catalog.generate_markdown(
        markdown_folder_paths_to_include=markdown_folder_paths_to_include,
        add_children_in_folder_pages=add_children_in_folder_pages, 
    )
    config_file = f"catalogs/{catalog_name}/mkdocs.yml"
    if not os.path.isfile(config_file):
        raise CatalogException(f"Missing config file {config_file}")
    print_info(f"Building site from mardown files into {catalog.folder}/site")
    exec(f"mkdocs build --config-file {config_file}")
    print_info(
        f"Serving website. Open this url in your browser --> http://localhost:{port} !"
    )
    exec(f"python -m http.server {port} --directory {catalog.folder}/site")


@cli.group()
def deploy():
    """
    Deploy documentation website
    """
    pass


@deploy.command()
@click.argument("catalog_name")
@handle_error
def github_pages(catalog_name):
    """
    Deploy documentation website on GitHub pages
    """
    catalog = Catalog(catalog_name)
    config_file = f"catalogs/{catalog_name}/mkdocs.yml"
    if not os.path.isfile(config_file):
        raise CatalogException(f"Missing config file {config_file}")
    print_info("Deploying site to GitHub pages")
    exec(f"mkdocs gh-deploy --config-file {config_file} --force")


@deploy.command()
@click.argument("catalog_name")
@handle_error
def gcs(catalog_name):
    """
    Deploy documentation website on a Google Cloud Storage bucket
    """
    catalog = Catalog(catalog_name)
    config_file = f"catalogs/{catalog_name}/mkdocs.yml"
    if not os.path.isdir(f"{catalog.folder}/site"):
        raise CatalogException(
            f"`{catalog.folder}/site` folder does not exist. Please build it with `build` command"
        )
    if not os.path.isfile(config_file):
        raise CatalogException(f"Missing config file {config_file}")
    config = load_yaml_file(config_file)
    site_url = config["site_url"]
    destination = site_url.split("://")[1]
    destination = destination + ("/" if not destination.endswith("/") else "")
    print_info(f"Copying site to destination `{destination}`")
    exec(f"gcloud storage cp -r {catalog.folder}/site/* gs://{destination}")
