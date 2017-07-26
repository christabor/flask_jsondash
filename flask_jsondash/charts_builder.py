# -*- coding: utf-8 -*-

"""
flask_jsondash.charts_builder
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The chart blueprint that houses all functionality.

:copyright: (c) 2016 by Chris Tabor.
:license: MIT, see LICENSE for more details.
"""

import json
import os
import uuid
from collections import namedtuple, defaultdict
from datetime import datetime as dt

import jinja2
from flask import (Blueprint, current_app, flash, redirect, render_template,
                   request, send_from_directory, url_for)

from flask_jsondash import static, templates

from . import db
from .settings import CHARTS_CONFIG
from .schema import (
    validate_raw_json, InvalidSchemaError,
)

TEMPLATE_DIR = os.path.dirname(templates.__file__)
STATIC_DIR = os.path.dirname(static.__file__)

# Internally required libs that are also shared in `settings.py` for charts.
# These follow the same format as what is loaded in `get_active_assets`
# so that shared libraries are loaded in the same manner for simplicty
# and prevention of duplicate loading. Note these are just LABELS, not files.
REQUIRED_STATIC_FAMILES = ['D3']

Paginator = namedtuple('Paginator',
                       'count per_page curr_page num_pages next limit skip')

charts = Blueprint(
    'jsondash',
    __name__,
    template_folder=TEMPLATE_DIR,
    static_url_path=STATIC_DIR,
    static_folder=STATIC_DIR,
)
default_config = dict(
    JSONDASH_FILTERUSERS=False,
    JSONDASH_GLOBALDASH=False,
    JSONDASH_GLOBAL_USER='global',
    JSONDASH_PERPAGE=25,
)
adapter = db.get_db_handler()


def auth(**kwargs):
    """Check if general auth functions have been specified.

    Checks for either a global auth (if authtype is None), or
    an action specific auth (specified by authtype).
    """
    if 'JSONDASH' not in current_app.config:
        return True
    if 'auth' not in current_app.config['JSONDASH']:
        return True
    authtype = kwargs.pop('authtype')
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

    Args:
        key (None, optional): A key to look up in global config.
        exclude (list, optional): A list of fields to exclude when
            retrieving metadata.

    Returns:
        _metadata (dict): The metadata configuration.
    """
    _metadata = dict()
    conf = current_app.config
    conf_metadata = conf.get('JSONDASH', {}).get('metadata')
    # Also useful for getting arbitrary configuration keys.
    if key is not None:
        if key in conf_metadata:
            return conf_metadata[key]()
        else:
            return None
    # Update all metadata values if the function exists.
    for k, func in conf_metadata.items():
        if k in exclude:
            continue
        _metadata[k] = conf_metadata[k]()
    return _metadata


def setting(name, default=None):
    """A simplified getter for namespaced flask config values.

    Args:
        name (str): A setting to retrieve the value for.
        default (None, optional): A default value to fall back to
            if not specified.
    Returns:
        str: A value from the app config.
    """
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
        docs_url=('https://github.com/christabor/flask_jsondash/'
                  'blob/master/docs/'),
        embeddable=request.args.get('embeddable', False),
        demo_mode=request.args.get('jsondash_demo_mode', False),
        global_dashuser=setting('JSONDASH_GLOBAL_USER'),
        global_dashboards=setting('JSONDASH_GLOBALDASH'),
        username=metadata(key='username') if filter_user else None,
        filter_dashboards=filter_user,
    )


@jinja2.contextfilter
@charts.app_template_filter('get_dims')
def get_dims(_, config):
    """Extract the dimensions from config data. This allows
    for overrides for edge-cases to live in one place.
    """
    if not all([
        'width' in config,
        'height' in config,
        'dataSource' in config,
        config.get('dataSource') != '',
        config.get('dataSource') is not None,
    ]):
        raise ValueError('Invalid config!')
    fixed_layout = str(config.get('width')).startswith('col-')
    if config.get('type') == 'youtube':
        # Override all width settings if fixed grid layout
        if fixed_layout:
            width = config['width'].replace('col-', '')
            return dict(width=width, height=int(config['height']))
        # We get the dimensions for the widget from YouTube instead,
        # which handles aspect ratios, etc... and is likely what the user
        # wanted to specify since they will be entering in embed code from
        # Youtube directly.
        padding_w = 20
        padding_h = 60
        embed = config['dataSource'].split(' ')
        w = int(embed[1].replace('width=', '').replace('"', ''))
        h = int(embed[2].replace('height=', '').replace('"', ''))
        return dict(width=w + padding_w, height=h + padding_h)
    return dict(width=config['width'], height=config['height'])


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
    return send_from_directory(STATIC_DIR, filename)


def get_all_assets():
    """Load ALL asset files for css/js from config."""
    cssfiles, jsfiles = [], []
    for c in CHARTS_CONFIG.values():
        if c['css_url'] is not None:
            cssfiles += c['css_url']
        if c['js_url'] is not None:
            jsfiles += c['js_url']
    return dict(
        css=cssfiles,
        js=jsfiles
    )


def get_active_assets(families):
    """Given a list of chart families, determine what needs to be loaded."""
    families += REQUIRED_STATIC_FAMILES  # Always load internal, shared libs.
    assets = dict(css=[], js=[])
    families = set(families)
    for family, data in CHARTS_CONFIG.items():
        if family in families:
            # Also add all dependency assets.
            if data['dependencies']:
                for dep in data['dependencies']:
                    assets['css'] += [
                        css for css in CHARTS_CONFIG[dep]['css_url']
                        if css not in assets['css']]

                    assets['js'] += [
                        js for js in CHARTS_CONFIG[dep]['js_url']
                        if js not in assets['js']
                    ]
            assets['css'] += [
                css for css in data['css_url'] if css not in assets['css']]
            assets['js'] += [
                js for js in data['js_url'] if js not in assets['js']]
    assets['css'] = list(assets['css'])
    assets['js'] = list(assets['js'])
    return assets


def paginator(page=0, per_page=None, count=None):
    """Get pagination calculations in a compact format."""
    if count is None:
        count = adapter.count()
    if page is None:
        page = 0
    if per_page is None:
        per_page = setting('JSONDASH_PERPAGE')
    per_page = per_page if per_page > 2 else 2  # Prevent division errors
    curr_page = page - 1 if page > 0 else 0
    num_pages = count // per_page
    rem = count % per_page
    extra_pages = 2 if rem else 1
    pages = list(range(1, num_pages + extra_pages))
    skip = curr_page * per_page
    return Paginator(
        limit=per_page,
        per_page=per_page,
        curr_page=curr_page,
        skip=skip,
        next=min([skip + per_page, count]),
        num_pages=pages,
        count=count,
    )


def get_num_rows(viewconf):
    """Get the number of rows for a layout if it's using fixed grid format.

    Args:
        viewconf (dict): The dashboard configuration

    Returns:
        int: returned if the number of modules can be determined
        None: returned if viewconf is invalid or the layout type
            does not support rows.
    """
    if viewconf is None:
        return None
    layout = viewconf.get('layout', 'freeform')
    if layout == 'freeform':
        return None
    return len([m['row'] for m in viewconf.get('modules')])


def order_sort(item):
    """Attempt to sort modules by order keys.

    Always returns an integer for compatibility.

    Args:
        item (dict): The module to sort

    Returns:
        int: The sort order integer, or -1 if the item cannot be sorted.
    """
    if item is None or item.get('order') is None:
        return -1
    try:
        return int(item['order'])
    except (ValueError, TypeError):
        return -1


def sort_modules(viewjson):
    """Sort module data in various ways.

    If the layout is freeform, sort by default order in a shallow list.
    If the layout is fixed grid, sort by default order, nested in a list
        for each row - e.g. [[{}, {}], [{}]]
        for row 1 (2 modules) and row 2 (1 module)
    """
    items = sorted(viewjson['modules'], key=order_sort)
    if viewjson.get('layout', 'freeform') == 'freeform':
        return items
    # Sort them by and group them by rows if layout is fixed grid
    # Create a temporary dict to hold the number of rows
    modules = list({int(item['row']) - 1: [] for item in items}.values())
    for module in items:
        modules[int(module['row']) - 1].append(module)
    return modules


def get_categories():
    """Get all categories."""
    views = list(adapter.filter({}, {'category': 1}))
    return set([
        v['category'] for v in views if v.get('category')
        not in [None, 'uncategorized']
    ])


def categorize_views(views):
    """Return a categorized version of the views.

    Categories are determined by the view category key, if present.
    If not present, then the view is bucketed into a general bucket.

    Args:
        views (list): The list of views.
    Returns:
        dict: The categorized version
    """
    buckets = defaultdict(list)
    for view in views:
        try:
            buckets[view.get('category', 'uncategorized')].append(view)
        except:
            continue
    for cat, view in buckets.items():
        buckets[cat] = sorted(view, key=lambda v: v['name'].lower())
    return buckets


@charts.route('/charts', methods=['GET'])
@charts.route('/charts/', methods=['GET'])
def dashboard():
    """Load all views."""
    opts = dict()
    views = []
    # Allow query parameter overrides.
    page = int(request.args.get('page', 0))
    per_page = int(request.args.get('per_page', setting('JSONDASH_PERPAGE')))
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
        pagination = paginator(count=len(views), page=page, per_page=per_page)
        opts.update(limit=pagination.limit, skip=pagination.skip)
        views = views[pagination.skip:pagination.next]
    else:
        pagination = None
    categorized = categorize_views(views)
    kwargs = dict(
        total=len(views),
        views=categorized,
        view=None,
        paginator=pagination,
        creating=True,
        can_edit_global=auth(authtype='edit_global'),
        total_modules=sum([
            len(view.get('modules', [])) for view in views
            if isinstance(view, dict)
        ]),
    )
    return render_template('pages/charts_index.html', **kwargs)


@charts.route('/charts/<c_id>', methods=['GET'])
def view(c_id):
    """Load a json view config from the DB."""
    if not auth(authtype='view', view_id=c_id):
        flash('You do not have access to view this dashboard.', 'error')
        return redirect(url_for('jsondash.dashboard'))
    viewjson = adapter.read(c_id=c_id)
    if not viewjson:
        flash('Could not find view: {}'.format(c_id), 'error')
        return redirect(url_for('jsondash.dashboard'))
    # Remove _id, it's not JSON serializeable.
    if '_id' in viewjson:
        viewjson.pop('_id')
    if 'modules' not in viewjson:
        flash('Invalid configuration - missing modules.', 'error')
        return redirect(url_for('jsondash.dashboard'))
    # Chart family is encoded in chart type value for lookup.
    active_charts = [v.get('family') for v in viewjson['modules']
                     if v.get('family') is not None]
    # If the logged in user is also the creator of this dashboard,
    # let me edit it. Otherwise, defer to any user-supplied auth function
    # for this specific view.
    if metadata(key='username') == viewjson.get('created_by'):
        can_edit = True
    else:
        can_edit = auth(authtype='edit_others', view_id=c_id)
    # Backwards compatible layout type
    layout_type = viewjson.get('layout', 'freeform')
    kwargs = dict(
        id=c_id,
        view=viewjson,
        categories=get_categories(),
        num_rows=None if layout_type == 'freeform' else get_num_rows(viewjson),
        modules=sort_modules(viewjson),
        assets=get_active_assets(active_charts),
        can_edit=can_edit,
        can_edit_global=auth(authtype='edit_global'),
        is_global=is_global_dashboard(viewjson),
    )
    return render_template('pages/chart_detail.html', **kwargs)


@charts.route('/charts/<c_id>/delete', methods=['POST'])
def delete(c_id):
    """Delete a json dashboard config."""
    dash_url = url_for('jsondash.dashboard')
    if not auth(authtype='delete'):
        flash('You do not have access to delete dashboards.', 'error')
        return redirect(dash_url)
    adapter.delete(c_id)
    flash('Deleted dashboard "{}"'.format(c_id))
    return redirect(dash_url)


@charts.route('/charts/<c_id>/update', methods=['POST'])
def update(c_id):
    """Normalize the form POST and setup the json view config object."""
    if not auth(authtype='update'):
        flash('You do not have access to update dashboards.', 'error')
        return redirect(url_for('jsondash.dashboard'))
    viewjson = adapter.read(c_id=c_id)
    if not viewjson:
        flash('Could not find view: {}'.format(c_id), 'error')
        return redirect(url_for('jsondash.dashboard'))
    form_data = request.form
    view_url = url_for('jsondash.view', c_id=c_id)
    edit_raw = 'edit-raw' in request.form
    now = str(dt.now())
    if edit_raw:
        try:
            conf = form_data.get('config')
            data = validate_raw_json(conf, date=now, id=c_id)
            data = db.reformat_data(data, c_id)
        except InvalidSchemaError as e:
            flash(str(e), 'error')
            return redirect(view_url)
        except (TypeError, ValueError) as e:
            flash('Invalid JSON config. "{}"'.format(e), 'error')
            return redirect(view_url)
    else:
        modules = db.format_charts(form_data)
        layout = form_data['mode']
        # Disallow any values if they would cause an invalid layout.
        if layout == 'grid' and modules and modules[0].get('row') is None:
            flash('Cannot use grid layout without '
                  'specifying row(s)! Edit JSON manually '
                  'to override this.', 'error')
            return redirect(view_url)
        category = form_data.get('category', '')
        category_override = form_data.get('category_new', '')
        category = category_override if category_override != '' else category
        data = dict(
            category=category if category != '' else 'uncategorized',
            name=form_data['name'],
            layout=layout,
            modules=modules,
            id=c_id,
            date=now,
        )
    # Update metadata, but exclude some fields that should never
    # be overwritten by user, once the view has been created.
    data.update(**metadata(exclude=['created_by']))
    # Possibly override global user, if configured and valid.
    data.update(**check_global())
    # Update db
    if edit_raw:
        adapter.update(c_id, data=data, fmt_charts=False)
    else:
        adapter.update(c_id, data=data)
    flash('Updated view "{}"'.format(c_id))
    return redirect(view_url)


def is_global_dashboard(view):
    """Check if a dashboard is considered global.

    Args:
        view (dict): The dashboard configuration

    Returns:
        bool: If all criteria was met to be included as a global dashboard.
    """
    return all([
        setting('JSONDASH_GLOBALDASH'),
        view.get('created_by') == setting('JSONDASH_GLOBAL_USER'),
    ])


def check_global():
    """Allow overriding of the user by making it global.

    This also checks if the setting is enabled for the app,
    otherwise it will not allow it.

    Returns:
        dict: A dictionary with certain global flags overriden.
    """
    global_enabled = setting('JSONDASH_GLOBALDASH')
    global_flag = request.form.get('is_global') is not None
    can_make_global = auth(authtype='edit_global')
    if all([global_flag, global_enabled, can_make_global]):
        return dict(created_by=setting('JSONDASH_GLOBAL_USER'))
    return dict()


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
        modules=db.format_charts(data),
        date=str(dt.now()),
        id=new_id,
        layout=data.get('mode', 'grid'),
    )
    d.update(**metadata())
    # Possibly override global user, if configured and valid.
    d.update(**check_global())
    # Add to DB
    adapter.create(data=d)
    flash('Created new dashboard "{}"'.format(data['name']))
    return redirect(url_for('jsondash.view', c_id=new_id))


@charts.route('/charts/<c_id>/clone', methods=['POST'])
def clone(c_id):
    """Clone a json view config from the DB."""
    if not auth(authtype='clone'):
        flash('You do not have access to clone dashboards.', 'error')
        return redirect(url_for('jsondash.dashboard'))
    viewjson = adapter.read(c_id=c_id)
    if not viewjson:
        flash('Could not find view: {}'.format(c_id), 'error')
        return redirect(url_for('jsondash.dashboard'))
    # Update some fields.
    newname = 'Clone of {}'.format(viewjson['name'])
    data = dict(
        name=newname,
        modules=viewjson['modules'],
        date=str(dt.now()),
        id=str(uuid.uuid1()),
        layout=viewjson['layout'],
    )
    data.update(**metadata())
    # Add to DB
    adapter.create(data=data)
    flash('Created new dashboard clone "{}"'.format(newname))
    return redirect(url_for('jsondash.view', c_id=data['id']))
