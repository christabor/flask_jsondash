# -*- coding: utf-8 -*-

"""The chart blueprint that houses all functionality."""

import json
import os
import uuid
from datetime import datetime as dt

from flask_jsondash import static, templates

from flask import (
    Blueprint,
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
    if 'JSONDASH' not in current_app.config:
        return False
    if 'auth' not in current_app.config['JSONDASH']:
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


def get_metadata(key=None):
    """An abstraction around misc. metadata.

    This allows loose coupling for enabling and setting
    metadata for each chart.
    """
    metadata = dict()
    conf = current_app.config
    conf_metadata = conf.get('JSONDASH', {}).get('metadata', None)
    # Also useful for getting arbitrary configuration keys.
    if key is not None:
        if key in conf_metadata:
            return conf_metadata[key]()
        else:
            return None
    # Update all metadata values if the function exists.
    for k, func in conf_metadata.items():
        metadata[k] = conf_metadata[k]()
    return metadata


@charts.route('/jsondash/<path:filename>')
def _static(filename):
    """Send static files directly for this blueprint."""
    return send_from_directory(static_dir, filename)


@charts.context_processor
def _ctx():
    """Inject any context needed for this blueprint."""
    filter_user = current_app.config.get('JSONDASH_FILTERUSERS', False)
    global_dashboards = current_app.config.get('JSONDASH_GLOBALDASH', True)
    global_dashuser = current_app.config.get('JSONDASH_GLOBAL_USER', 'global')
    return dict(
        charts_config=CHARTS_CONFIG,
        page_title='dashboards',
        global_dashuser=global_dashuser,
        global_dashboards=global_dashboards,
        username=get_metadata(key='username') if filter_user else None,
        filter_dashboards=filter_user,
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
    view_url = url_for('jsondash.view', id=c_id)
    if 'edit-raw' in request.form:
        try:
            data = json.loads(request.form.get('config'))
            data = adapter.reformat_data(data, c_id)
            data.update(**get_metadata())
            # Update db
            adapter.update(c_id, data=data, fmt_modules=False)
        except (TypeError, ValueError):
            flash('Invalid JSON config.', 'error')
            return redirect(view_url)
    else:
        # Update db
        d = dict(
            name=data['name'],
            modules=adapter._format_modules(data),
            date=dt.now(),
            id=data['id'],
        )
        d.update(**get_metadata())
        adapter.update(c_id, data=d)
    flash('Updated view "{}"'.format(c_id))
    return redirect(view_url)


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
    d.update(**get_metadata())
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
    data.update(**get_metadata())
    # Add to DB
    adapter.create(data=data)
    return redirect(url_for('jsondash.view', id=data['id']))
