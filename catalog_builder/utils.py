import os
import urllib.request
import subprocess
import functools
import traceback
import sys

import click
import requests
import yaml


class CatalogException(Exception):
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


def exec(command):
    print_command(command)
    try:
        return subprocess.check_output(command, shell=True).decode().strip()
    except subprocess.CalledProcessError as e:
        raise CatalogException("See error above. " + e.output.decode(errors="ignore").strip())




def load_yaml_file(filename):
    class SafeLoaderIgnoreUnknown(yaml.SafeLoader):
        def ignore_unknown(self, node):
            return None 

    SafeLoaderIgnoreUnknown.add_constructor(None, SafeLoaderIgnoreUnknown.ignore_unknown)
    content = open(filename, encoding='utf-8').read()
    return yaml.load(content, Loader=SafeLoaderIgnoreUnknown)