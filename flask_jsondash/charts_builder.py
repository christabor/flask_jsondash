# -*- coding: utf-8 -*-

"""
flask_jsondash.charts_builder
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The chart blueprint that houses all functionality.
"""

import json
import os
import uuid
from collections import namedtuple
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

Paginator = namedtuple('Paginator',
                       'count per_page curr_page num_pages limit skip')

charts = Blueprint(
    'jsondash',
    __name__,
    template_folder=template_dir,
    static_url_path=static_dir,
    static_folder=static_dir,
)
default_config = dict(
    JSONDASH_FILTERUSERS=False,
    JSONDASH_GLOBALDASH=False,
    JSONDASH_GLOBAL_USER='global',
    JSONDASH_PERPAGE=25,
)


def auth(**kwargs):
    """Check if general auth functions have been specified.

    Checks for either a global auth (if authtype is None), or
    an action specific auth (specified by authtype).
    """
    authtype = kwargs.pop('authtype')
    if 'JSONDASH' not in current_app.config:
        return True
    if 'auth' not in current_app.config['JSONDASH']:
        return True
    auth_conf = current_app.config.get('JSONDASH').get('auth')
    # If the user didn't supply an auth function, assume true.
    if authtype not in auth_conf:
        return True
    # Only perform the user-supplied check
    # if the authtype is actually enabled.
    return auth_conf[authtype](**kwargs)


def metadata(key=None, exclude=[]):
    """An abstraction around misc. metadata.

    This allows loose coupling for enabling and setting
    metadata for each chart.
    """
    _metadata = dict()
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
        if k in exclude:
            pass
        _metadata[k] = conf_metadata[k]()
    return _metadata


def setting(name, default=None):
    """A simplified getter for namespaced flask config values."""
    if default is None:
        default = default_config.get(name)
    return current_app.config.get(name, default)


def local_static(chart_config, static_config):
    """Convert remote cdn urls to local urls, based on user provided paths.

    The filename must be identical to the one specified in the
    `settings.py` configuration.

    So, for example:
    '//cdnjs.cloudflare.com/foo/bar/foo.js'
    becomes
    '/static/js/vendor/foo.js'
    """
    js_path = static_config.get('js_path')
    css_path = static_config.get('css_path')
    for family, config in chart_config.items():
        if config['js_url']:
            for i, url in enumerate(config['js_url']):
                url = '{}{}'.format(js_path, url.split('/')[-1])
                config['js_url'][i] = url_for('static', filename=url)
        if config['css_url']:
            for i, url in enumerate(config['css_url']):
                url = '{}{}'.format(css_path, url.split('/')[-1])
                config['css_url'][i] = url_for('static', filename=url)
    return chart_config


@charts.context_processor
def ctx():
    """Inject any context needed for this blueprint."""
    filter_user = setting('JSONDASH_FILTERUSERS')
    static = setting('JSONDASH').get('static')
    # Rewrite the static config paths to be local if the overrides are set.
    config = (CHARTS_CONFIG if not static
              else local_static(CHARTS_CONFIG, static))
    return dict(
        static_config=static,
        charts_config=config,
        page_title='dashboards',
        global_dashuser=setting('JSONDASH_GLOBAL_USER'),
        global_dashboards=setting('JSONDASH_GLOBALDASH'),
        username=metadata(key='username') if filter_user else None,
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


@charts.route('/jsondash/<path:filename>')
def _static(filename):
    """Send static files directly for this blueprint."""
    return send_from_directory(static_dir, filename)


def paginator(count=None):
    """Get pagination calculations in a compact format."""
    if count is None:
        count = adapter.count()
    per_page = setting('JSONDASH_PERPAGE')
    # Allow query parameter overrides.
    per_page = int(request.args.get('per_page', 0)) or per_page
    per_page = per_page if per_page > 2 else 2  # Prevent division errors etc
    curr_page = int(request.args.get('page', 1)) - 1
    num_pages = count // per_page
    rem = count % per_page
    extra_pages = 2 if rem else 1
    pages = range(1, num_pages + extra_pages)
    return Paginator(
        limit=per_page,
        per_page=per_page,
        curr_page=curr_page,
        skip=curr_page * per_page,
        num_pages=pages,
        count=count,
    )


@charts.route('/charts/', methods=['GET'])
def dashboard():
    """Load all views."""
    opts = dict()
    views = []
    if setting('JSONDASH_FILTERUSERS'):
        opts.update(filter=dict(created_by=metadata(key='username')))
        views = list(adapter.read(**opts))
        if setting('JSONDASH_GLOBALDASH'):
            opts.update(
                filter=dict(created_by=setting('JSONDASH_GLOBAL_USER')))
            views += list(adapter.read(**opts))
    else:
        views = list(adapter.read(**opts))
    if views:
        pagination = paginator(count=len(views))
        opts.update(limit=pagination.limit, skip=pagination.skip)
    else:
        pagination = None
    kwargs = dict(
        views=views,
        view=None,
        paginator=pagination,
        total_modules=sum([len(view['modules']) for view in views]),
    )
    return render_template('pages/charts_index.html', **kwargs)


@charts.route('/charts/<id>', methods=['GET'])
def view(id):
    """Load a json view config from the DB."""
    if not auth(authtype='view'):
        flash('You do not have access to view this dashboard.', 'error')
        return redirect(url_for('jsondash.dashboard'))
    viewjson = adapter.read(c_id=id)
    if not viewjson:
        flash('Could not find view: {}'.format(id), 'error')
        return redirect(url_for('jsondash.dashboard'))
    # Remove _id, it's not JSON serializeable.
    viewjson.pop('_id')
    # Chart family is encoded in chart type value for lookup.
    active_charts = [v.get('family') for
                     v in viewjson['modules'] if v.get('family')]
    kwargs = dict(id=id, view=viewjson, active_charts=active_charts)
    return render_template('pages/chart_detail.html', **kwargs)


@charts.route('/charts/<c_id>/delete', methods=['POST'])
def delete(c_id):
    """Delete a json dashboard config."""
    dash_url = url_for('jsondash.dashboard')
    if not auth(authtype='delete'):
        flash('You do not have access to delete dashboards.', 'error')
        return redirect(dash_url)
    adapter.delete(c_id)
    flash('Deleted dashboard {}'.format(c_id))
    return redirect(dash_url)


@charts.route('/charts/update', methods=['POST'])
def update():
    """Normalize the form POST and setup the json view config object."""
    if not auth(authtype='update'):
        flash('You do not have access to update dashboards.', 'error')
        return redirect(url_for('jsondash.dashboard'))
    data = request.form
    c_id = data['id']
    view_url = url_for('jsondash.view', id=c_id)
    if 'edit-raw' in request.form:
        try:
            data = json.loads(request.form.get('config'))
            data = adapter.reformat_data(data, c_id)
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
            id=c_id,
        )
        # Update metadata, but exclude some fields that should never
        # be overwritten once the view has been created.
        d.update(**metadata(exclude=['created_by']))
        adapter.update(c_id, data=d)
    flash('Updated view "{}"'.format(c_id))
    return redirect(view_url)


@charts.route('/charts/create', methods=['POST'])
def create():
    """Normalize the form POST and setup the json view config object."""
    if not auth(authtype='create'):
        flash('You do not have access to create dashboards.', 'error')
        return redirect(url_for('jsondash.dashboard'))
    data = request.form
    new_id = str(uuid.uuid1())
    d = dict(
        name=data['name'],
        modules=adapter._format_modules(data),
        date=dt.now(),
        id=new_id,
    )
    d.update(**metadata())
    # Add to DB
    adapter.create(data=d)
    flash('Created new view "{}"'.format(data['name']))
    return redirect(url_for('jsondash.view', id=new_id))


@charts.route('/charts/clone/<c_id>', methods=['POST'])
def clone(c_id):
    """Clone a json view config from the DB."""
    if not auth(authtype='clone'):
        flash('You do not have access to clone dashboards.', 'error')
        return redirect(url_for('jsondash.dashboard'))
    viewjson = adapter.read(c_id=c_id)
    if not viewjson:
        flash('Could not find view: {}'.format(id), 'error')
        return redirect(url_for('jsondash.dashboard'))
    # Update some fields.
    data = dict(
        name='Clone of {}'.format(viewjson['name']),
        modules=viewjson['modules'],
        date=dt.now(),
        id=str(uuid.uuid1()),
    )
    data.update(**metadata())
    # Add to DB
    adapter.create(data=data)
    return redirect(url_for('jsondash.view', id=data['id']))
