"""Utilities for dealing with static assets -- downloading, etc..."""

import os

import requests
import click

from settings import CHARTS_CONFIG


@click.command()
@click.option('--js',
              default=True,
              help='Download JS assets?')
@click.option('--css',
              default=True,
              help='Download CSS assets?')
def get_remote_assets(css, js):
    """Download all static assets for the library to local source."""
    print('Downloading remote assets: JS? {} / CSS? {}'.format(css, js))
    for family, config in CHARTS_CONFIG.items():
        if js and config['js_url'] is not None:
            for url in config['js_url']:
                file = url.split('/')[-1]
                print(file)
                host = url.replace(file, '')
                print('Downloading: {file} from {host}'.format(
                    file=file, host=host))
                path = 'flask_jsondash/static/js/vendor/{file}'.format(
                    file=file)
                os.system('curl -XGET {url} > {path}'.format(
                    url=url, path=path))
        # if js:


if __name__ == '__main__':
    get_remote_assets()
