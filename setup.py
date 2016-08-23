"""Setup for Flask Jsondash."""

from glob import glob
import os
from setuptools import setup, find_packages

SRCDIR = '.'
folder = os.path.abspath(os.path.dirname(__file__))
template_start = '{}/flask_jsondash/templates'.format(folder)
static_start = '{}/flask_jsondash/static'.format(folder)


def get_all_files(pattern, start_dir=None):
    """Get all subdirectory files specified by `pattern`."""
    paths = []
    if start_dir is None:
        start_dir = os.getcwd()
    for root, dirs, files in os.walk(start_dir):
        globbed = glob(os.path.join(root, pattern))
        paths.extend(globbed)
    return paths


def readme():
    """Grab the long README file."""
    try:
        with open('README.md', 'r') as fobj:
            return fobj.read()
    except IOError:
        try:
            with open('README.rst', 'r') as fobj:
                return fobj.read()
        except IOError:
            return 'No README specified.'


def get_requires():
    """Extract the requirements from a standard requirements.txt file."""
    path = '{}/requirements.txt'.format(folder)
    with open(path) as reqs:
        return [req for req in reqs.readlines() if req]


# Recursively retrieve all package data (static files)
# Make sure static data exists, except uncompiled source (sass, etc)
js_files = get_all_files('*.js', start_dir='{}/js'.format(static_start))
css_files = get_all_files('*.css', start_dir='{}/css'.format(static_start))
html_files = get_all_files('*.html', start_dir=template_start)
staticfiles = js_files + css_files + html_files

setup(
    name='flask_jsondash',
    version='3.1.0',
    description=('Easily configurable, chart dashboards from any '
                 'arbitrary API endpoint. JSON config only. Ready to go.'),
    long_description=readme(),
    author='Chris Tabor',
    author_email='dxdstudio@gmail.com',
    url='https://github.com/christabor/flask_jsondash',
    license='MIT',
    classifiers=[
        'Topic :: Software Development',
        'Programming Language :: Python :: 2.7',
    ],
    package_dir={'': SRCDIR},
    packages=find_packages(SRCDIR, exclude=['ez_setup', 'examples', 'tests']),
    package_data=dict(flask_jsondash=staticfiles),
    zip_safe=False,
    include_package_data=True,
)
