# -*- coding: utf-8 -*-

"""
flask_jsondash.model_factories
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Data generation utilities for all charts and dashboards.

:copyright: (c) 2016 by Chris Tabor.
:license: MIT, see LICENSE for more details.
"""

import json
from datetime import datetime as dt
from random import choice, randrange
from uuid import uuid1

import click
from werkzeug.datastructures import ImmutableMultiDict

from . import db, settings

adapter = db.get_db_handler()


def get_random_group():
    """Return a random namespaced group of charts.

    Returns:
        str: A random chart name.

    Examples:
        >>> get_random_group()
        >>> {'charts': [...], 'dependencies', 'js_url': '...', ...}
    """
    return choice(list(settings.CHARTS_CONFIG.values()))


def get_random_chart(group):
    """Get a random chart from a specific chart sub-group.

    Args:
        group (dict): A group from the global chart settings config.
    """
    return choice(list(group['charts']))


def make_fake_dashboard(name='Random chart', max_charts=10):
    """Generate fake dashboard data with a specific number of random charts.

    Args:
        name (str): The name of the new dashboard (default: {'Random chart'})
        max_charts (int): Max number of charts to make (default: {10})

    Returns:
        dict: The chart configuration.
    """
    charts = ImmutableMultiDict([
        make_fake_chart_data() for _ in range(max_charts)]
    )
    return dict(
        name=name,
        created_by='global',
        date=dt.now(),
        modules=db.format_charts(charts),
        id=str(uuid1()),
    )


def make_fake_chart_data(**kwargs):
    """Return chart data in required format.

    Args:
        name (None, optional): The name of the chart.
        height (None, optional): The height of the chart.
        width (None, optional): The width of the chart.
        data_source (None, optional): The data source (url) for the chart.

    Returns:
        tuple: A 2-tuple of type (string_label, jsonstring) for the chart.

    Examples:
        >>> make_fake_chart_date(width=10, height=10, name='foo')
        >>> ('foo', '{"name": "foo", "height": 10, "width": 10}')
    """
    _uuid = str(uuid1())
    # All of these chart types have example endpoints to use locally.
    chart = choice(['bar', 'line', 'step', 'area'])
    will_use_inputs = randrange(1, 100) > 50
    url = 'http://127.0.0.1:5004/bar'
    config = dict(
        name=kwargs.get('name'),
        width=kwargs.get('width', randrange(200, 2000)),
        height=kwargs.get('height', randrange(200, 2000)),
        type=chart,
        family='C3',
        dataSource=kwargs.get('data_source', url),
        guid=_uuid,
    )
    if will_use_inputs:
        config.update(
            inputs=dict(
                btn_classes=['btn', 'btn-info', 'btn-sm'],
                submit_text='Submit',
                help_text='Change a value',
                options=[
                    dict(type='number', name='range', label='Number'),
                ]
            )
        )
    return (
        'module_{}'.format(_uuid),
        json.dumps(config)
    )


@click.command()
@click.option('--records',
              default=10,
              help='Number of records to insert fake dashboard data into DB.')
@click.option('--max-charts',
              default=5,
              help='Number of charts per dashboard to create.')
def insert_dashboards(records, max_charts):
    """Insert a number of dashboard records into the database."""
    for i in range(records):
        data = make_fake_dashboard(
            name='Test chart #{}'.format(i),
            max_charts=max_charts)
        adapter.create(data=data)


def delete_all():
    """Delete all dashboards."""
    adapter.delete_all()


if __name__ == '__main__':
    insert_dashboards()
