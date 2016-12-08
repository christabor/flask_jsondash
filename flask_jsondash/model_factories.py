# -*- coding: utf-8 -*-

"""
flask_jsondash.model_factories
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Data generation utilities for all charts and dashboards.
"""

import json
from datetime import datetime as dt
from random import choice, randrange
from uuid import uuid1

import click

from werkzeug.datastructures import ImmutableMultiDict

from . import db_adapters
from . import settings


def get_random_group():
    """Return a random namespaced group of charts."""
    return choice(list(settings.CHARTS_CONFIG.values()))


def get_random_chart(group):
    """Get a random chart from a specific chart sub-group."""
    return choice(list(group['charts']))


def make_fake_dashboard(name='Random chart', max_charts=10):
    """Generate fake dashboard data with a specific number of random charts."""
    charts = ImmutableMultiDict([
        make_fake_chart_data() for _ in range(max_charts)]
    )
    return dict(
        name=name,
        created_by='global',
        date=dt.now(),
        modules=db_adapters._format_modules(charts),
        id=str(uuid1()),
    )


def make_fake_chart_data(**kwargs):
    """Return chart data in required format."""
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
        db_adapters.create(data=data)


def delete_all():
    """Delete all dashboards."""
    db_adapters.delete_all()


if __name__ == '__main__':
    insert_dashboards()
