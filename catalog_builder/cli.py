import os

import click
from click_help_colors import HelpColorsGroup
import yaml

from .catalogs import Catalog, CatalogException
from .utils import handle_error, print_info, download_github_folder, exec


@click.group(
    cls=HelpColorsGroup,
    help_headers_color='yellow',
    help_options_color='cyan'
)
def cli():
    pass


@cli.command()
@click.argument('catalog_name')
@handle_error
def download(catalog_name):
    '''
    Download CATALOG_NAME configuration folder from `catalog_builder` GitHub
    '''
    if os.path.isdir(f'catalogs/{catalog_name}'):
        raise CatalogException(f'`catalogs/{catalog_name}` folder already exists. If you wish to download it again please remove the folder beforehand.')
    download_github_folder(f'catalogs/{catalog_name}')
    print_success(f'Downloaded `catalogs/{catalog_name}`')


@cli.command()
@click.argument('catalog_name')
@handle_error
def build(catalog_name):
    '''
    Build CATALOG_NAME catalog (builds docs/ and site/)
    '''
    catalog = Catalog(catalog_name)
    print_info(f'Generating mardown files into {catalog.folder}/docs')
    catalog.generate_markdown()
    config_file = f'catalogs/{catalog_name}/mkdocs.yml'
    if not os.path.isfile(config_file):
        raise CatalogException(f'Missing config file {config_file}')
    print_info(f'Building site from mardown files into {catalog.folder}/site')
    exec(f'mkdocs build --config-file {config_file}')


@cli.command()
@click.argument('catalog_name')
@handle_error
def serve(catalog_name):
    '''
    Serve CATALOG_NAME website on http://localhost:8000
    '''
    catalog = Catalog(catalog_name)
    if not os.path.isdir(f'{catalog.folder}/site'):
        raise CatalogException(f'`{catalog.folder}/site` folder does not exist. Please build it with `build` command')
    print_info(f'Serving website. Open this url in your browser --> http://localhost:8000 !')
    exec(f'python -m http.server --directory {catalog.folder}/site')


@cli.group()
def deploy():
    '''
    Deploy documentation website
    '''
    pass


@deploy.command()
@click.argument('catalog_name')
def github_pages(catalog_name):
    '''
    Deploy documentation website on GitHub pages
    '''
    catalog = Catalog(catalog_name)
    config_file = f'catalogs/{catalog_name}/mkdocs.yml'
    if not os.path.isfile(config_file):
        raise CatalogException(f'Missing config file {config_file}')
    print_info(f'Deploying site to GitHub pages')
    exec(f'mkdocs gh-deploy --config-file {config_file} --force')


# @deploy.command()
# @click.argument('catalog_name')
# def gcs(catalog_name):
#     '''
#     Deploy documentation website on a Google Cloud Storage bucket
#     '''
#     catalog = Catalog(catalog_name)
#     config_file = f'catalogs/{catalog_name}/mkdocs.yml'
#     if not os.path.isdir(f'{catalog.folder}/site'):
#         raise CatalogException(f'`{catalog.folder}/site` folder does not exist. Please build it with `build` command')
#     if not os.path.isfile(config_file):
#         raise CatalogException(f'Missing config file {config_file}')
#     config = yaml.safe_load(open(config_file, encoding='utf-8').read())
#     breakpoint()
#     print_info(f'Deploying site to GitHub pages')
#     exec(f'mkdocs gh-deploy --config-file {config_file} --force')

#     gcloud storage cp catalogs/simple/site/pypi/distribution_metadata/index.html  gs://catalogs.unytics.io/bigquery_public_data/pypi/distribution_metadata/index.html