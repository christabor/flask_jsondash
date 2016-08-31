"""Setup for Flask Jsondash."""

import os
from setuptools import setup

SRCDIR = '.'
folder = os.path.abspath(os.path.dirname(__file__))
template_start = '{}/flask_jsondash/templates'.format(folder)
static_start = '{}/flask_jsondash/static'.format(folder)


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


setup(
    name='flask_jsondash',
    version='3.8.1',
    description=('Easily configurable, chart dashboards from any '
                 'arbitrary API endpoint. JSON config only. Ready to go.'),
    long_description=readme(),
    author='Chris Tabor',
    author_email='dxdstudio@gmail.com',
    url='https://github.com/christabor/flask_jsondash',
    license='MIT',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    install_requires=get_requires(),
    package_dir={'flask_jsondash': 'flask_jsondash'},
    packages=['flask_jsondash'],
    zip_safe=False,
    include_package_data=True,
)
