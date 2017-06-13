"""Setup for Flask Jsondash."""

import os

from setuptools import setup

SRCDIR = '.'
folder = os.path.abspath(os.path.dirname(__file__))
test_requirements = [
    'pytest==3.0',
    'pytest-cov==2.4',
    'pyquery==1.2',
]
requirements = [
    'click==6.6',
    'Flask',
    'cerberus',
    'pymongo==3.3.0',
]


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


setup(
    name='flask_jsondash',
    version='6.2.3',
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
    tests_require=test_requirements,
    install_requires=requirements,
    package_dir={'flask_jsondash': 'flask_jsondash'},
    packages=['flask_jsondash'],
    zip_safe=False,
    include_package_data=True,
)
