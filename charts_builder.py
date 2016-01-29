# -*- coding: utf-8 -*-

import json
from datetime import datetime as dt
import jinja2
from flask import render_template, request, flash, redirect
from flask import Blueprint
from pymongo import MongoClient

client = MongoClient()
db = client['buildalytics']
collection = db['views']


charts = Blueprint('charts_builder', __name__, template_folder='templates')


@jinja2.contextfilter
@charts.app_template_filter('jsonstring')
def jsonstring(ctx, string):
    # Format view json module data for template use - it's automatically
    # converted to unicode key/value pairs,
    # which is undesirable for the template.
    return json.dumps(string).replace('\'', '"').replace(
        'u"', '"').replace('"{"', '{"').replace('"}"', '"}')


def _format_modules(data):
    modules = []
    # Format modules data for json usage
    for item in data:
        if item.startswith('module_'):
            print(data[item])
            val_json = json.loads(data[item])
            modules.append(val_json)
    return modules


@charts.route('/charts/', methods=['GET'])
def dashboard():
    """Load all views."""
    return render_template('index.html', views=collection.find())


@charts.route('/charts/custom', methods=['GET'])
def custom_widget():
    """Provides custom widget functionality for built-in app widgets.
    These are specified in the c.dataSource argument in your config,
    and map to a template specified within the `templates` directory.
    """
    widget = request.args.get('template', None)
    assert widget is not None, 'Must have a valid widget'
    return render_template(widget)


@charts.route('/charts/<id>', methods=['GET'])
def view(id):
    """Load a json view config via mongoDB. Other json adapters
    (PSQL/Cassandra, etc...) can be easily adapted here."""
    viewjson = collection.find_one({'name': id})
    if not viewjson:
        flash('Could not find view: {}'.format(id))
        return redirect('/charts/')
    viewjson.pop('_id')
    return render_template('view.html', id=id, view=viewjson)


@charts.route('/charts/update', methods=['POST'])
def update():
    """Normalize the form POST and setup the json view config object.
    This is then saved to MongoDB."""
    data = request.form
    save_conf = {
        '$set': {
            'name': data['name'],
            'modules': _format_modules(data),
            'date': dt.now()
        }
    }
    # Update mongo
    collection.update({'name': data['name']}, save_conf)
    flash('Updated view "{}"'.format(data['name']))
    return redirect('/charts/{}'.format(data['name']))


@charts.route('/charts/create', methods=['POST'])
def create():
    """Normalize the form POST and setup the json view config object.
    This is then saved to MongoDB."""
    data = request.form

    d = {
        'name': data['name'],
        'modules': _format_modules(data),
        'date': dt.now()
    }
    # Add to mongo
    collection.insert(d)
    flash('Created new view "{}"'.format(data['name']))
    return redirect('/charts/')
