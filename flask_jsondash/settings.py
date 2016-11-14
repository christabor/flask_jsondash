# -*- coding: utf-8 -*-

"""
flask_jsondash.settings
~~~~~~~~~~~~~~~~~~~~~~~

App/blueprint wide settings.
"""

import os

# DB Settings - Defaults to values specific for Mongo,
# but Postgresql is also supported.
DB_URI = os.environ.get('CHARTS_DB_HOST', 'localhost')
DB_PORT = int(os.environ.get('CHARTS_DB_PORT', 27017))
DB_NAME = os.environ.get('CHARTS_DB_DB', 'charts')
# This name is used for table/collection,
# regardless of Postgresql or Mongodb usage.
DB_TABLE = os.environ.get('CHARTS_DB_TABLE', 'views')
ACTIVE_DB = os.environ.get('CHARTS_ACTIVE_DB', 'mongo').lower()

"""
Chart configuration below -- this is essential to making the frontend work.
Default values have been added, but you can change them by importing your
own override (see bottom).

Configuration:

'charts' is a list of 2-tuples, where:

1. The first index is the type -- this MUST NOT CHANGE!
2. The second index is the label -- This is configurable.

'css_url'/'js_url' can be relative or absolute paths.

"""

CHARTS_CONFIG = {
    'C3': {
        'charts': [
            ('line', 'Line chart'),
            ('bar', 'Bar chart'),
            ('timeseries', 'Timeseries chart'),
            ('step', 'Step chart'),
            ('pie', 'Pie chart'),
            ('area', 'Area chart'),
            ('donut', 'Donut chart'),
            ('spline', 'Spline chart'),
            ('gauge', 'Gauge chart'),
            ('scatter', 'Scatter chart'),
            ('area-spline', 'Area spline chart'),
        ],
        'dependencies': ['D3'],
        'js_url': ['//cdnjs.cloudflare.com/ajax/libs/c3/0.4.11/c3.min.js'],
        'css_url': ['//cdnjs.cloudflare.com/ajax/libs/c3/0.4.11/c3.min.css'],
        'enabled': True,
        'help_link': 'http://c3js.org/reference.html',
    },
    'D3': {
        'charts': [
            ('radial-dendrogram', 'Radial Dendrogram'),
            ('dendrogram', 'Dendrogram'),
            ('treemap', 'Treemap'),
            ('voronoi', 'Voronoi'),
            ('circlepack', 'Circle Pack'),
        ],
        'dependencies': None,
        'js_url': ['//cdnjs.cloudflare.com/ajax/libs/d3/3.5.16/d3.min.js'],
        'css_url': None,
        'enabled': True,
        'help_link': 'https://github.com/d3/d3/wiki',
    },
    'Basic': {
        'charts': [
            ('custom', 'Custom embed of any arbitrary code.'),
            ('iframe', 'Embedded iframe.'),
            ('number', 'A single number representing some aggregate value.'),
            ('youtube', 'An embedded YouTube video.'),
        ],
        'dependencies': None,
        'js_url': None,
        'css_url': None,
        'enabled': True
    },
    'DataTable': {
        'charts': [
            ('datatable', 'A table of data, with sorting and filtering.'),
        ],
        'dependencies': None,
        'js_url': [
            ('//cdnjs.cloudflare.com/ajax/libs/datatables/1.10.12/js/'
             'jquery.dataTables.min.js'),
            ('//cdnjs.cloudflare.com/ajax/libs/datatables/1.10.10/js/'
             'dataTables.bootstrap.min.js')
        ],
        'css_url': [
            ('//cdnjs.cloudflare.com/ajax/libs/datatables/1.10.10/css/'
             'dataTables.bootstrap.min.css'),
        ],
        'enabled': True,
        'help_link': 'https://datatables.net/reference/index',
    },
    'Timeline': {
        'charts': [
            ('timeline', 'A timeline'),
        ],
        'dependencies': None,
        'js_url': ['//cdn.knightlab.com/libs/timeline3/latest/js/timeline.js'],
        'css_url': [
            '//cdn.knightlab.com/libs/timeline3/latest/css/timeline.css'],
        'enabled': True,
        'help_link': 'https://timeline.knightlab.com/docs/',
    },
    'Venn': {
        'charts': [
            ('venn', 'A venn diagram'),
        ],
        'dependencies': ['D3'],
        'js_url': ['//cdn.rawgit.com/benfred/venn.js/master/venn.js'],
        'css_url': None,
        'enabled': True,
        'help_link': 'https://github.com/benfred/venn.js/',
    },
    'Graph': {
        'charts': [
            ('graph', 'Graph'),
        ],
        'dependencies': ['D3'],
        'js_url': [
            ('//cdnjs.cloudflare.com/ajax/libs/'
             'dagre-d3/0.4.17/dagre-d3.min.js'),
            ('//raw.githubusercontent.com/cpettitt/graphlib-dot/'
             'master/dist/graphlib-dot.min.js'),
        ],
        'css_url': None,
        'enabled': True,
        'help_link': 'https://github.com/cpettitt/dagre-d3/wiki'
    },
    'Sparklines': {
        'charts': [
            ('sparklines-line', 'Sparkline Line'),
            ('sparklines-bar', 'Sparkline Bar'),
            ('sparklines-tristate', 'Sparkline Tristate'),
            ('sparklines-discrete', 'Sparkline Discrete'),
            ('sparklines-bullet', 'Sparkline Bullet'),
            ('sparklines-pie', 'Sparkline Pie'),
            ('sparklines-box', 'Sparkline Box'),
        ],
        'dependencies': None,
        'js_url': [
            ('//cdnjs.cloudflare.com/ajax/libs/jquery-sparklines/'
             '2.1.2/jquery.sparkline.min.js'),
        ],
        'css_url': None,
        'enabled': True,
        'help_link': 'http://omnipotent.net/jquery.sparkline/#s-docs',
    },
    'PlotlyStandard': {
        'charts': [
            ('plotly-any', 'Any'),
        ],
        'dependencies': None,
        'js_url': [
            '//cdn.plot.ly/plotly-latest.min.js',
        ],
        'css_url': None,
        'enabled': True,
        'help_link': 'https://plot.ly/javascript/',
    },
}

# Import optional chart overrides.
try:
    from settings_override import *
except ImportError:
    print('Could not find override settings. Using default settings.')
