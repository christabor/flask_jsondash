#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
flask_jsondash.data_utils.filetree
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A utility for getting d3 friendly hierarchical data structures
from the list of files and directories on a given path.

Re-purposed from: github.com/christabor/MoAL/blob/master/MOAL/get_file_tree.py

:copyright: (c) 2016 by Chris Tabor.
:license: MIT, see LICENSE for more details.
"""

import errno
import json
import os
from pprint import pprint

import click

# Py2/3 compat.
try:
    _unicode = unicode
except NameError:
    _unicode = str


def path_hierarchy(path):
    """Create a json representation of a filesystem tree.

    Format is suitable for d3.js application.

    Taken from:
    http://unix.stackexchange.com/questions/164602/
        how-to-output-the-directory-structure-to-json-format
    """
    valid_path = any([isinstance(path, _unicode), isinstance(path, str)])
    assert valid_path, 'Requires a valid path!'
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
@click.option('--indent', '-i',
              default=4,
              help='How far to indent if using json.')
@click.option('--jsonfile', '-j',
              default=None,
              help='Output specified file as json.')
@click.option('--path', '-p',
              default='.',
              help='The starting path')
def get_tree(path, jsonfile, ppr, indent):
    """CLI wrapper for recursive function."""
    res = path_hierarchy(path)
    if jsonfile is not None:
        with open(jsonfile, 'w') as jsonfile:
            jsonfile.write(json.dumps(res, indent=indent))
        return
    if ppr:
        pprint(res, indent=indent)
    else:
        print(res)


if __name__ == '__main__':
    get_tree()
