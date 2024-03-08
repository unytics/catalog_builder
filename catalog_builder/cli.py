import os
import functools
import traceback
import sys
import urllib.request

import requests
import click
from click_help_colors import HelpColorsGroup

from .catalogs import Catalog, CatalogException


@click.group(
    cls=HelpColorsGroup,
    help_headers_color='yellow',
    help_options_color='cyan'
)
def cli():
    pass


def print_color(msg):
    click.echo(click.style(msg, fg='cyan'))

def print_success(msg):
    click.echo(click.style(f'SUCCESS: {msg}', fg='green'))

def print_info(msg):
    click.echo(click.style(f'INFO: {msg}', fg='yellow'))

def print_command(msg):
    click.echo(click.style(f'INFO: `{msg}`', fg='magenta'))

def print_warning(msg):
    click.echo(click.style(f'WARNING: {msg}', fg='cyan'))


def handle_error(f):

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except (AssertionError, CatalogException) as e:
            click.echo(click.style(f'ERROR: {e}', fg='red'))
            sys.exit()
        except Exception as e:
            click.echo(click.style(f'ERROR: {e}', fg='red'))
            print(traceback.format_exc())
            sys.exit()

    return wrapper





@cli.command()
@click.argument('catalog_name')
@handle_error
def download(catalog_name):
    '''
    Download CATALOG_NAME configuration folder from `catalog_builder` GitHub
    '''
    if os.path.isdir(f'catalogs/{catalog_name}'):
        raise CatalogException(f'`catalogs/{catalog_name}` folder already exists. If you wish to download it again please remove the folder beforehand.')

    def download_github_folder(folder):
        url = f'https://api.github.com/repos/unytics/catalog_builder/contents/{folder}'
        resp = requests.get(url)
        if not resp.ok:
            raise CatalogException(f'Could not list files in {folder} catalog: {resp.text}')
        files = resp.json()
        for file in files:
            if file['type'] == 'file':
                try:
                    file_folder = '/'.join(file['path'].split('/')[:-1])
                    os.makedirs(file_folder, exist_ok=True)
                    urllib.request.urlretrieve(file['download_url'], file['path'])
                except Exception as e:
                    raise CatalogException(f"Could not download file at url `{file['download_url']}`. Reason: {e}")
            elif file['type'] == 'dir':
                download_github_folder(file['path'])

    download_github_folder(f'catalogs/{catalog_name}')
    print_success(f'Downloaded `catalogs/{catalog_name}`')

