# -*- coding: utf-8 -*-

"""
flask_jsondash.db
~~~~~~~~~~~~~~~~~~~~~~~~~~

A translation adapter for transparent operations between storage types.

:copyright: (c) 2016 by Chris Tabor.
:license: MIT, see LICENSE for more details.
"""

import json

from datetime import datetime as dt

from pymongo import MongoClient

from . import mongo_adapter
from . import settings

DB_NAME = settings.ACTIVE_DB


def reformat_data(data, c_id):
    """Format/clean existing config data to be re-inserted into database."""
    data.update(dict(id=c_id, date=dt.now()))
    return data


def format_charts(data):
    """Form chart POST data for JSON usage within db."""
    modules = []
    for item in data:
        if item.startswith('module_'):
            val_json = json.loads(data[item])
            modules.append(val_json)
    return modules


def get_db_handler():
    """Get the appropriate db adapter."""
    if DB_NAME == 'mongo':
        client = MongoClient(host=settings.DB_URI, port=settings.DB_PORT)
        conn = client[settings.DB_NAME]
        coll = conn[settings.DB_TABLE]
        return mongo_adapter.Db(client, conn, coll, format_charts)
    else:
        raise NotImplementedError(
            'Mongodb is the only supported database right now.')
