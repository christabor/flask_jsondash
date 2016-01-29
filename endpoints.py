# -*- coding: utf-8 -*-

from flask import Flask
import json
import random as rand
from pymongo import MongoClient
from flask.ext.cors import cross_origin
from flask.ext.cors import CORS
import time


client = MongoClient()
db = client['buildalytics']
collection = db['views']
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'NOTSECURELOL'
app.debug = True

"""
https://flask-cors.readthedocs.org/en/latest/
"""


@cross_origin()
@app.route('/timeline/')
def timeline():
    with open('timeline3.json', 'r') as timelinejson:
        return timelinejson.read()
    return json.dumps({})


@cross_origin()
@app.route('/test4/')
def test4():
    # time.sleep(rand.randrange(1, 4))
    return json.dumps({
        "name": "foo",
        "children": [{
            "name": '---foo---', "size": i
        } for i in range(0, 30)]
    })


@cross_origin()
@app.route('/test3/')
def test3():
    # time.sleep(rand.randrange(1, 4))
    return json.dumps({
        "name": "foo",
        "children": [{
            "name": '---foo---', "size": i
        } for i in range(0, 30)]
    })


@cross_origin()
@app.route('/test1/')
def test1():
    # Simulate slow connection
    # time.sleep(rand.randrange(1, 4))
    return json.dumps([
        ['data1'] + [rand.randrange(0, 100) for _ in range(12)],
        ['data2'] + [rand.randrange(0, 100) for _ in range(12)],
        ['data3'] + [rand.randrange(0, 100) for _ in range(12)],
        ['data4'] + [rand.randrange(0, 100) for _ in range(12)],
    ])


@cross_origin()
@app.route('/test2/')
def test2():
    # time.sleep(rand.randrange(1, 4))
    return json.dumps([
        ['data3'] + [rand.randrange(0, 100) for _ in range(12)],
        ['data4'] + [rand.randrange(0, 100) for _ in range(12)],
    ])


if __name__ == '__main__':
    app.run(debug=True, port=5001)
