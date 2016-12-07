#!/usr/bin/env python

"""
A utility for getting d3 friendly hierarchical data structures
from the list of files and directories on a given path.

Re-purposed from:
github.com/christabor/MoAL/blob/master/MOAL/get_file_tree.py
"""

import os
from pprint import pprint
import errno
import json

import click


def path_hierarchy(path):
    """Create a json representation of a file tree.

    Format is suitable for d3.js application.

    Taken from:
    http://unix.stackexchange.com/questions/164602/
        how-to-output-the-directory-structure-to-json-format
    """
    name = os.path.basename(path)
    hierarchy = {
        'type': 'folder',
        'name': name,
        'path': path,
    }
    try:
        hierarchy['children'] = [
            path_hierarchy(os.path.join(path, contents))
            for contents in os.listdir(path)
        ]
    except OSError as e:
        if e.errno != errno.ENOTDIR:
            raise
        hierarchy['type'] = 'file'
    return hierarchy


@click.command()
@click.option('--ppr/--no-ppr',
              default=False,
              help='Pretty-print results.')
@click.option('--jsonfile', '-j',
              default=None,
              help='Output specified file as json.')
@click.option('--path', '-p',
              default='.',
              help='The starting path')
def get_tree(path, jsonfile, ppr):
    """CLI wrapper for recursive function."""
    res = path_hierarchy(path)
    if jsonfile is not None:
        with open(jsonfile, 'wb+') as jsonfile:
            jsonfile.write(json.dumps(res, indent=4))
        return
    if ppr:
        pprint(res)
    else:
        print(res)


if __name__ == '__main__':
    get_tree()
