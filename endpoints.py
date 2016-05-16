"""A separate Flask app that serves fake endpoints for demo purposes."""

# -*- coding: utf-8 -*-

import json
import os
from random import randrange as rr
from random import choice, random
import time

from flask import (
    Flask,
    abort,
)
from flask.ext.cors import CORS
from flask.ext.cors import cross_origin

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'NOTSECURELOL'
app.debug = True

cwd = os.getcwd()


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
@app.route('/deadend/')
def test_die():
    """Fake endpoint that ends in a random 50x error."""
    # Simulate slow connection
    time.sleep(random())
    abort(choice([500, 501, 502, 503, 504]))


@cross_origin()
@app.route('/test4/')
def test4():
    """Fake endpoint."""
    # Simulate slow connection
    time.sleep(random())
    return json.dumps({
        "name": "foo",
        "children": [{
            "name": '---foo---', "size": i
        } for i in range(0, 30)]
    })


@cross_origin()
@app.route('/test3/')
def test3():
    """Fake endpoint."""
    # Simulate slow connection
    time.sleep(random())
    return json.dumps({
        "name": "foo",
        "children": [{
            "name": '---foo---', "size": i
        } for i in range(0, 30)]
    })


@cross_origin()
@app.route('/test1/')
def test1():
    """Fake endpoint."""
    # Simulate slow connection
    time.sleep(random())
    return json.dumps([
        ['data1'] + [rr(0, 100) for _ in range(12)],
        ['data2'] + [rr(0, 100) for _ in range(12)],
        ['data3'] + [rr(0, 100) for _ in range(12)],
        ['data4'] + [rr(0, 100) for _ in range(12)],
    ])


@cross_origin()
@app.route('/test2/')
def test2():
    """Fake endpoint."""
    # Simulate slow connection
    time.sleep(random())
    return json.dumps([
        ['data3'] + [rr(0, 100) for _ in range(12)],
        ['data4'] + [rr(0, 100) for _ in range(12)],
    ])


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


@app.route('/dendrogram', methods=['GET'])
def dendro():
    """Fake endpoint."""
    with open('{}/examples/flare.json'.format(cwd), 'r') as djson:
        return djson.read()
    return json.dumps({})


if __name__ == '__main__':
    app.run(debug=True, port=5004)
