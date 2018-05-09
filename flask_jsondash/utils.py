# -*- coding: utf-8 -*-

"""
flask_jsondash.utils
~~~~~~~~~~~~~~~~~~~~

General utils for handling data within the blueprint.

:copyright: (c) 2016 by Chris Tabor.
:license: MIT, see LICENSE for more details.
"""

from collections import defaultdict, namedtuple

from flask import current_app

from flask_jsondash import db

adapter = db.get_db_handler()
Paginator = namedtuple('Paginator',
                       'count per_page curr_page num_pages next limit skip')

default_config = dict(
    JSONDASH_FILTERUSERS=False,
    JSONDASH_GLOBALDASH=False,
    JSONDASH_GLOBAL_USER='global',
    JSONDASH_PERPAGE=25,
)


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


def is_global_dashboard(view):
    """Check if a dashboard is considered global.

    Args:
        view (dict): The dashboard configuration

    Returns:
        bool: If all criteria was met to be included as a global dashboard.
    """
    global_user = setting('JSONDASH_GLOBAL_USER')
    return all([
        setting('JSONDASH_GLOBALDASH'),
        view.get('created_by') == global_user,
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
        except Exception:
            continue
    for cat, view in buckets.items():
        buckets[cat] = sorted(view, key=lambda v: v['name'].lower())
    return buckets


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
