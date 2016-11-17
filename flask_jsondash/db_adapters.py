# -*- coding: utf-8 -*-

"""
flask_jsondash.db_adapters
~~~~~~~~~~~~~~~~~~~~~~~~~~

A translation adapter for making queries between storage types.

Types are either:
1. PostgreSQL json fields
2. MongoDB collections.
"""

import json
from datetime import datetime as dt

from pymongo import MongoClient

from . import settings

DB_NAME = settings.ACTIVE_DB


if DB_NAME == 'mongo':
    client = MongoClient(host=settings.DB_URI, port=settings.DB_PORT)
    conn = client[settings.DB_NAME]
    coll = conn[settings.DB_TABLE]
else:
    raise NotImplemented('PostgreSQL is not yet supported.')


def reformat_data(data, c_id):
    """Format/clean existing config data to be re-inserted into database."""
    data.update(dict(id=c_id, date=dt.now()))
    return data


def _format_modules(data):
    """Form module data for JSON."""
    modules = []
    # Format modules data for json usage
    for item in data:
        if item.startswith('module_'):
            val_json = json.loads(data[item])
            modules.append(val_json)
    return modules


def count(**kwargs):
    """Standard db count."""
    if DB_NAME == 'mongo':
        return coll.count(**kwargs)
    else:
        raise NotImplemented('{} is not supported.'.format(DB_NAME))


def read(**kwargs):
    """Read a record."""
    if DB_NAME == 'mongo':
        if kwargs.get('c_id') is None:
            return coll.find(**kwargs)
        else:
            return coll.find_one(dict(id=kwargs.pop('c_id')))
    else:
        raise NotImplemented('{} is not supported.'.format(DB_NAME))


def update(c_id, data=None, fmt_modules=True):
    """Update a record."""
    if data is None:
        return
    if DB_NAME == 'mongo':
        modules = _format_modules(data) if fmt_modules else data.get('modules')
        save_conf = {
            '$set': {
                'name': data.get('name', 'NONAME'),
                'modules': modules,
                'date': dt.now()
            }
        }
        save_conf['$set'].update(**data)
        coll.update(dict(id=c_id), save_conf)
    else:
        raise NotImplemented('{} is not supported.'.format(DB_NAME))


def create(data=None):
    """Add a new record."""
    if data is None:
        return
    if DB_NAME == 'mongo':
        coll.insert(data)
    else:
        raise NotImplemented('{} is not supported.'.format(DB_NAME))


def delete(c_id):
    """Delete a record."""
    if DB_NAME == 'mongo':
        coll.delete_one(dict(id=c_id))
    else:
        raise NotImplemented('{} is not supported.'.format(DB_NAME))


def delete_all():
    """Delete ALL records. Separated function for safety.

    This should never be used for production.
    """
    if DB_NAME == 'mongo':
        coll.remove()
    else:
        raise NotImplemented('{} is not supported.'.format(DB_NAME))
