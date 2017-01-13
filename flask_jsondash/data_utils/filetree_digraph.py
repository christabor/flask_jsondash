#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
flask_jsondash.data_utils.filetree_digraph
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A utility for getting digraph friendly data structures
from the list of files and directories on a given path.

:copyright: (c) 2016 by Chris Tabor.
:license: MIT, see LICENSE for more details.
"""

import errno
import os

import click

# Py2/3 compat.
try:
    _unicode = unicode
except NameError:
    _unicode = str


def path_hierarchy(path, hierarchy=[], prev=None):
    """Create a dotfile representation of a filesystem tree.

    Format is suitable for graphviz applications.
    """
    valid_path = any([isinstance(path, _unicode), isinstance(path, str)])
    assert valid_path, 'Requires a valid path!'
    name = os.path.basename(path)
    if prev is not None:
        prev = str(prev)
        # Ensure empty names or current dir '.' are not added.
        if all([prev != '', prev != '.']):
            # Wrap in quotes to prevent dot parsing errors.
            hierarchy.append('"{}" -> "{}"'.format(prev, name))
    try:
        # Recursively add all subfolders and files.
        hierarchy += [
            path_hierarchy(os.path.join(path, contents), prev=name)
            for contents in os.listdir(path)
        ]
    except OSError as e:
        if e.errno != errno.ENOTDIR:
            raise
    return hierarchy


def make_dotfile(path):
    """Generate the recursive path and then format into dotfile format."""
    _res = [w for w in path_hierarchy(path) if not isinstance(w, list)]
    res = 'digraph {\n'
    for item in _res:
        if item.startswith(' ->'):
            continue
        res += '\t{};\n'.format(item)
    res += '}\n'
    return res


@click.command()
@click.option('--dot', '-d',
              default=None,
              help='Output specified file as a dotfile.')
@click.option('--path', '-p',
              default='.',
              help='The starting path')
def get_dotfile_tree(path, dot):
    """CLI wrapper for existing functions."""
    res = make_dotfile(path)
    if path == '.':
        raise ValueError('Running in the same directory when no'
                         ' folders are present does not make sense.')
    if dot is not None:
        with open(dot, 'w') as dotfile:
            dotfile.write(res)
        return
    else:
        print(res)


if __name__ == '__main__':
    get_dotfile_tree()
