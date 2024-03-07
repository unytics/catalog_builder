import functools
import traceback
import sys

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
@click.argument('name')
@handle_error
def get_example(name):
    '''
    Create CONNECTION
    '''
    catalog = Catalog(name)
    catalog.generate_markdown()
    print_success(f'Created connection `{name}`')

