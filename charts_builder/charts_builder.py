# -*- coding: utf-8 -*-

"""The chart blueprint that houses all functionality."""

import json
import uuid
from datetime import datetime as dt

from flask import Blueprint
from flask import (
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
import jinja2

import db_adapters as adapter
from settings import (
    CHARTS_CONFIG,
    HEARTBEAT,
)

charts = Blueprint(
    'charts_builder',
    __name__,
    template_folder='templates',
    static_url_path='/flask_jsondash/static',
    static_folder='static',
)


@charts.context_processor
def _ctx():
    """Inject any context needed for this blueprint."""
    return dict(
        charts_config=CHARTS_CONFIG,
        charts_heartbeat=HEARTBEAT,
    )


@jinja2.contextfilter
@charts.app_template_filter('jsonstring')
def jsonstring(ctx, string):
    """Format view json module data for template use.

    It's automatically converted to unicode key/value pairs,
    which is undesirable for the template.
    """
    return json.dumps(string).replace('\'', '"').replace(
        'u"', '"').replace('"{"', '{"').replace('"}"', '"}')


@charts.route('/charts/', methods=['GET'])
def dashboard():
    """Load all views."""
    views = list(adapter.read())
    kwargs = dict(
        views=views,
        total_modules=sum([len(view['modules']) for view in views]),
    )
    return render_template('pages/charts_index.html', **kwargs)


@charts.route('/charts/<id>', methods=['GET'])
def view(id):
    """Load a json view config from the DB."""
    viewjson = adapter.read(c_id=id)
    if not viewjson:
        flash('Could not find view: {}'.format(id))
        return redirect(url_for('charts_builder.dashboard'))
    # Remove _id, it's not JSON serializeable.
    viewjson.pop('_id')
    return render_template('pages/chart_detail.html', id=id, view=viewjson)


@charts.route('/charts/<c_id>/delete', methods=['POST'])
def delete(c_id):
    """Delete a json dashboard config."""
    adapter.delete(c_id)
    flash('Deleted dashboard {}'.format(c_id))
    return redirect(url_for('charts_builder.dashboard'))


@charts.route('/charts/update', methods=['POST'])
def update():
    """Normalize the form POST and setup the json view config object."""
    data = request.form
    c_id = data['id']
    # Update db
    adapter.update(c_id, data=data)
    flash('Updated view "{}"'.format(c_id))
    return redirect(url_for('charts_builder.view', id=c_id))
    kwargs = dict(form=None)
    return redirect(url_for('charts_builder.index'), **kwargs)


@charts.route('/charts/create', methods=['POST'])
def create():
    """Normalize the form POST and setup the json view config object."""
    data = request.form
    d = dict(
        name=data['name'],
        modules=adapter._format_modules(data),
        date=dt.now(),
        id=str(uuid.uuid1()),
    )
    # Add to DB
    adapter.create(data=d)
    flash('Created new view "{}"'.format(data['name']))
    return redirect(url_for('charts_builder.dashboard'))


@charts.route('/charts/clone/<c_id>', methods=['POST'])
def clone(c_id):
    """Load a json view config from the DB."""
    viewjson = adapter.read(c_id=c_id)
    if not viewjson:
        flash('Could not find view: {}'.format(id))
        return redirect(url_for('charts_builder.dashboard'))
    # Update some fields.
    data = dict(
        name='Clone of {}'.format(viewjson['name']),
        modules=viewjson['modules'],
        data=dt.now(),
        id=str(uuid.uuid1()),
    )
    # Add to DB
    adapter.create(data=data)
    return redirect(url_for('charts_builder.view', id=data['id']))
