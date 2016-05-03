"""A separate Flask app that serves fake endpoints for demo purposes."""

# -*- coding: utf-8 -*-

import json
import random as rand
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


@cross_origin()
@app.route('/timeline/')
def timeline():
    """Fake endpoint."""
    with open('timeline3.json', 'r') as timelinejson:
        return timelinejson.read()
    return json.dumps({})


@cross_origin()
@app.route('/deadend/')
def test_die():
    """Fake endpoint that ends in a random 50x error."""
    # Simulate slow connection
    time.sleep(rand.random())
    abort(rand.choice([500, 501, 502, 503, 504]))


@cross_origin()
@app.route('/test4/')
def test4():
    """Fake endpoint."""
    # Simulate slow connection
    time.sleep(rand.random())
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
    time.sleep(rand.random())
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
    time.sleep(rand.random())
    return json.dumps([
        ['data1'] + [rand.randrange(0, 100) for _ in range(12)],
        ['data2'] + [rand.randrange(0, 100) for _ in range(12)],
        ['data3'] + [rand.randrange(0, 100) for _ in range(12)],
        ['data4'] + [rand.randrange(0, 100) for _ in range(12)],
    ])


@cross_origin()
@app.route('/test2/')
def test2():
    """Fake endpoint."""
    # Simulate slow connection
    time.sleep(rand.random())
    return json.dumps([
        ['data3'] + [rand.randrange(0, 100) for _ in range(12)],
        ['data4'] + [rand.randrange(0, 100) for _ in range(12)],
    ])


if __name__ == '__main__':
    app.run(debug=True, port=5001)
