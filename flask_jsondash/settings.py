# -*- coding: utf-8 -*-

"""
flask_jsondash.settings
~~~~~~~~~~~~~~~~~~~~~~~

App/blueprint wide settings.

:copyright: (c) 2016 by Chris Tabor.
:license: MIT, see LICENSE for more details.
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
        'dependencies': [],
        'js_url': ['//cdnjs.cloudflare.com/ajax/libs/d3/3.5.16/d3.min.js'],
        'css_url': [],
        'enabled': True,
        'help_link': 'https://github.com/d3/d3/wiki',
    },
    'WordCloud': {
        'charts': [
            ('wordcloud', 'Word Cloud'),
        ],
        'js_url': [
            ('//cdnjs.cloudflare.com/ajax/libs/d3-cloud/1.2.4/'
             'd3.layout.cloud.min.js'),
        ],
        'css_url': [],
        'enabled': True,
        'dependencies': ['D3'],
        'help_link': 'https://github.com/jasondavies/d3-cloud'
    },
    'Basic': {
        'charts': [
            ('custom', 'Custom direct loading of any arbitrary html.'),
            ('iframe', 'Embedded iframe.'),
            ('image', 'Image (inline embed)'),
            ('number', ('Single number (size autoscaled) representing '
                        'some aggregate value.')),
            ('youtube', 'YouTube video embedded as an iframe.'),
        ],
        'dependencies': [],
        'js_url': [],
        'css_url': [],
        'enabled': True,
        'help_link': ('https://github.com/christabor/flask_jsondash/blob/'
                      'master/docs/schemas.md'),
    },
    'Vega': {
        'charts': [
            ('vega-lite', 'vega-lite specification.'),
        ],
        'dependencies': ['D3'],
        'js_url': [
            ('//cdnjs.cloudflare.com/ajax/libs/vega/2.6.5/vega.min.js'),
            ('//cdnjs.cloudflare.com/ajax/libs/vega-lite/'
             '1.3.1/vega-lite.min.js'),
            ('//cdnjs.cloudflare.com/ajax/libs/vega-embed/'
             '2.2.0/vega-embed.min.js'),
        ],
        'css_url': [],
        'enabled': True,
        'help_link': 'https://vega.github.io/vega-lite/docs',
    },
    'DataTable': {
        'charts': [
            ('datatable', 'A table of data, with sorting and filtering.'),
        ],
        'dependencies': [],
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
            ('timeline', 'A timeline.js timeline'),
        ],
        'dependencies': [],
        'js_url': ['//cdn.knightlab.com/libs/timeline3/latest/js/timeline.js'],
        'css_url': [
            '//cdn.knightlab.com/libs/timeline3/latest/css/timeline.css'],
        'enabled': True,
        'help_link': 'https://timeline.knightlab.com/docs/',
    },
    'Venn': {
        'charts': [
            ('venn', 'A venn.js Venn or Euler diagram'),
        ],
        'dependencies': ['D3'],
        'js_url': ['//cdn.rawgit.com/benfred/venn.js/master/venn.js'],
        'css_url': [],
        'enabled': True,
        'help_link': 'https://github.com/benfred/venn.js/',
    },
    'SigmaJS': {
        'charts': [
            ('sigma', 'SigmaJS default json based graph'),
        ],
        'dependencies': [],
        'js_url': [
            '//cdnjs.cloudflare.com/ajax/libs/sigma.js/1.2.0/sigma.min.js',
        ],
        'css_url': [],
        'enabled': True,
        'help_link': 'http://sigmajs.org',
    },
    'Cytoscape': {
        'charts': [
            ('cytoscape', ('Cytoscape compatible json configuration '
                           '(core layouts only).')),
        ],
        'dependencies': [],
        'js_url': [
            ('//cdnjs.cloudflare.com/ajax/libs/cytoscape/'
             '3.1.0/cytoscape.min.js'),
        ],
        'css_url': [],
        'enabled': True,
        'help_link': 'http://js.cytoscape.org/'
    },
    'Graph': {
        'charts': [
            ('graph', 'Graph using the graphviz .dot specification'),
        ],
        'dependencies': ['D3'],
        'js_url': [
            ('//cdnjs.cloudflare.com/ajax/libs/'
             'dagre-d3/0.4.17/dagre-d3.min.js'),
            ('//raw.githubusercontent.com/cpettitt/graphlib-dot/'
             'master/dist/graphlib-dot.min.js'),
        ],
        'css_url': [],
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
        'dependencies': [],
        'js_url': [
            ('//cdnjs.cloudflare.com/ajax/libs/jquery-sparklines/'
             '2.1.2/jquery.sparkline.min.js'),
        ],
        'css_url': [],
        'enabled': True,
        'help_link': 'http://omnipotent.net/jquery.sparkline/#s-docs',
    },
    'PlotlyStandard': {
        'charts': [
            ('plotly-any', 'Plotly serializable specification'),
        ],
        'dependencies': [],
        'js_url': [
            '//cdn.plot.ly/plotly-latest.min.js',
        ],
        'css_url': [],
        'enabled': True,
        'help_link': 'https://plot.ly/javascript/',
    },
}
