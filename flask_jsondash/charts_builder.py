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
    current_app,
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


def auth_enabled(authtype=None):
    """Check if general auth functions have been specified.

    Checks for either a global auth (if authtype is None), or
    an action specific auth (specified by authtype).
    """
    if not all([
        'JSONDASH' in current_app.config,
        'auth' in current_app.config['JSONDASH']
    ]):
        return False
    auth_conf = current_app.config.get('JSONDASH').get('auth')
    if authtype is not None:
        return authtype in auth_conf
    return True


def auth_check(authtype, **kwargs):
    """Check if a user specified validator works for access to a given type.

    This does not check if a specific auth function was defined, and assumes
    that is done elsewhere.
    """
    return current_app.config['JSONDASH']['auth'][authtype](**kwargs)


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
        page_title='dashboards',
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
    if auth_enabled(authtype='view'):
        if not auth_check('view', view_id=id):
            flash('You do not have access to view this dashboard.', 'error')
            return redirect(url_for('jsondash.dashboard'))
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
    dash_url = url_for('jsondash.dashboard')
    if auth_enabled(authtype='delete'):
        if not auth_check('delete'):
            flash('You do not have access to delete dashboards.', 'error')
            return redirect(dash_url)
    adapter.delete(c_id)
    flash('Deleted dashboard {}'.format(c_id))
    return redirect(dash_url)


@charts.route('/charts/update', methods=['POST'])
def update():
    """Normalize the form POST and setup the json view config object."""
    if auth_enabled(authtype='update'):
        if not auth_check('update'):
            flash('You do not have access to update dashboards.', 'error')
            return redirect(url_for('jsondash.dashboard'))
    data = request.form
    c_id = data['id']
    # Update db
    adapter.update(c_id, data=data)
    flash('Updated view "{}"'.format(c_id))
    return redirect(url_for('jsondash.view', id=c_id))


@charts.route('/charts/create', methods=['POST'])
def create():
    """Normalize the form POST and setup the json view config object."""
    if auth_enabled(authtype='create'):
        if not auth_check('create'):
            flash('You do not have access to create dashboards.', 'error')
            return redirect(url_for('jsondash.dashboard'))
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
    if auth_enabled(authtype='clone'):
        if not auth_check('clone'):
            flash('You do not have access to clone dashboards.', 'error')
            return redirect(url_for('jsondash.dashboard'))
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
