"""A separate Flask app that serves fake endpoints for demo purposes."""

# -*- coding: utf-8 -*-

import json
import locale
import os
from datetime import timedelta as td
from datetime import datetime as dt
from random import randrange as rr
from random import choice, random
import time

from flask import (
    Flask,
    abort,
    request,
    render_template,
)
from flask.ext.cors import CORS
from flask.ext.cors import cross_origin

app = Flask('endpoints_test')
CORS(app)
app.config['SECRET_KEY'] = 'NOTSECURELOL'
app.debug = True

locale.setlocale(locale.LC_ALL, '')

cwd = os.getcwd()


def dates_list(max_dates=10):
    """Generate a timeseries dates list."""
    now = dt.now()
    return [str(now + td(days=i * 10))[0:10] for i in range(max_dates)]


def rr_list(max_range=10):
    """Generate a list of random integers."""
    return [rr(0, 100) for i in range(max_range)]


@cross_origin()
@app.route('/timeline/')
def timeline():
    """Fake endpoint."""
    with open('{}/examples/timeline3.json'.format(cwd), 'r') as timelinejson:
        return timelinejson.read()
    return json.dumps({})


@app.route('/dtable', methods=['GET'])
def dtable():
    """Fake endpoint."""
    with open('{}/examples/dtable.json'.format(os.getcwd()), 'r') as djson:
        return djson.read()
    return json.dumps({})


@cross_origin()
@app.route('/timeseries/')
def timeseries():
    """Fake endpoint."""
    return json.dumps({
        "dates": dates_list(),
        "line1": rr_list(max_range=10),
        "line2": rr_list(max_range=10),
        "line3": rr_list(max_range=10),
    })


@cross_origin()
@app.route('/gauge/')
def gauge():
    """Fake endpoint."""
    return json.dumps({'data': rr(1, 100)})


@cross_origin()
@app.route('/scatter/')
def scatter():
    """Fake endpoint."""
    with open('{}/examples/overrides.json'.format(cwd), 'r') as jsonfile:
        return jsonfile.read()
    return json.dumps(dict())


@cross_origin()
@app.route('/pie/')
def pie():
    """Fake endpoint."""
    letters = list('abcde')
    return json.dumps({'data {}'.format(name): rr(1, 100) for name in letters})


@cross_origin()
@app.route('/bar/')
def barchart():
    """Fake endpoint."""
    return json.dumps({
        "bar1": [1, 2, 30, 12, 100],
        "bar2": rr_list(max_range=5),
        "bar3": rr_list(max_range=5),
    })


@cross_origin()
@app.route('/line/')
def linechart():
    """Fake endpoint."""
    return json.dumps({
        "line1": [1, 4, 3, 10, 12, 14, 18, 10],
        "line2": [1, 2, 10, 20, 30, 6, 10, 12, 18, 2],
        "line3": rr_list(),
    })


@cross_origin()
@app.route('/singlenum/')
def singlenum():
    """Fake endpoint."""
    _min, _max = 10, 10000
    if 'sales' in request.args:
        val = locale.currency(float(rr(_min, _max)), grouping=True)
    else:
        val = rr(_min, _max)
    if 'negative' in request.args:
        val = '-{}'.format(val)
    return json.dumps(val)


@cross_origin()
@app.route('/deadend/')
def test_die():
    """Fake endpoint that ends in a random 50x error."""
    # Simulate slow connection
    time.sleep(random())
    abort(choice([500, 501, 502, 503, 504]))


@cross_origin()
@app.route('/venn/')
def test_venn():
    """Fake endpoint."""
    data = [
        {'sets': ['A'], 'size': rr(10, 100)},
        {'sets': ['B'], 'size': rr(10, 100)},
        {'sets': ['C'], 'size': rr(10, 100)},
        {'sets': ['A', 'B'], 'size': rr(10, 100)},
        {'sets': ['A', 'B', 'C'], 'size': rr(10, 100)},
    ]
    return json.dumps(data)


@app.route('/sparklines', methods=['GET'])
def sparklines():
    """Fake endpoint."""
    return json.dumps([rr(0, 100) for _ in range(20)])


@app.route('/circlepack', methods=['GET'])
def circlepack():
    """Fake endpoint."""
    with open('{}/examples/flare.json'.format(cwd), 'r') as djson:
        return djson.read()
    return json.dumps({})


@app.route('/treemap', methods=['GET'])
def treemap():
    """Fake endpoint."""
    with open('{}/examples/flare.json'.format(cwd), 'r') as djson:
        return djson.read()
    return json.dumps({})


@app.route('/map', methods=['GET'])
def datamap():
    """Fake endpoint."""
    return render_template('examples/map.html')


@app.route('/dendrogram', methods=['GET'])
def dendro():
    """Fake endpoint."""
    with open('{}/examples/flare.json'.format(cwd), 'r') as djson:
        return djson.read()
    return json.dumps({})


if __name__ == '__main__':
    app.run(debug=True, port=5004)
