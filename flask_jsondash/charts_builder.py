# -*- coding: utf-8 -*-

"""The chart blueprint that houses all functionality."""

import os
import json
import uuid
from datetime import datetime as dt

from flask_jsondash import templates
from flask_jsondash import static

from flask import Blueprint
from flask import (
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
import jinja2

import db_adapters as adapter
from settings import (
    CHARTS_CONFIG,
    HEARTBEAT,
)

template_dir = os.path.dirname(templates.__file__)
static_dir = os.path.dirname(static.__file__)

charts = Blueprint(
    'jsondash',
    __name__,
    template_folder=template_dir,
    static_url_path=static_dir,
    static_folder=static_dir,
)


@charts.route('/jsondash/<path:filename>')
def _static(filename):
    """Send static files directly for this blueprint."""
    return send_from_directory(static_dir, filename)


@charts.context_processor
def _ctx():
    """Inject any context needed for this blueprint."""
    return dict(
        charts_config=CHARTS_CONFIG,
        charts_heartbeat=HEARTBEAT,
    )


@jinja2.contextfilter
@charts.app_template_filter('jsonstring')
def jsonstring(ctx, data):
    """Format view json module data for template use.

    It's automatically converted to unicode key/value pairs,
    which is undesirable for the template.
    """
    if 'date' in data:
        data['date'] = str(data['date'])
    return json.dumps(data)


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
        return redirect(url_for('jsondash.dashboard'))
    # Remove _id, it's not JSON serializeable.
    viewjson.pop('_id')
    return render_template('pages/chart_detail.html', id=id, view=viewjson)


@charts.route('/charts/<c_id>/delete', methods=['POST'])
def delete(c_id):
    """Delete a json dashboard config."""
    adapter.delete(c_id)
    flash('Deleted dashboard {}'.format(c_id))
    return redirect(url_for('jsondash.dashboard'))


@charts.route('/charts/update', methods=['POST'])
def update():
    """Normalize the form POST and setup the json view config object."""
    data = request.form
    c_id = data['id']
    # Update db
    adapter.update(c_id, data=data)
    flash('Updated view "{}"'.format(c_id))
    return redirect(url_for('jsondash.view', id=c_id))
    kwargs = dict(form=None)
    return redirect(url_for('jsondash.index'), **kwargs)


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
    return redirect(url_for('jsondash.dashboard'))


@charts.route('/charts/clone/<c_id>', methods=['POST'])
def clone(c_id):
    """Clone a json view config from the DB."""
    viewjson = adapter.read(c_id=c_id)
    if not viewjson:
        flash('Could not find view: {}'.format(id))
        return redirect(url_for('jsondash.dashboard'))
    # Update some fields.
    data = dict(
        name='Clone of {}'.format(viewjson['name']),
        modules=viewjson['modules'],
        date=dt.now(),
        id=str(uuid.uuid1()),
    )
    # Add to DB
    adapter.create(data=data)
    return redirect(url_for('jsondash.view', id=data['id']))
