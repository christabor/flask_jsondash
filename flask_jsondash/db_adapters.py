"""A translation adapter for making queries between storage types.

Types are either:
1. PostgreSQL json fields
2. MongoDB collections.
"""

from datetime import datetime as dt
import json

from pymongo import MongoClient

import settings

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


def read(c_id=None):
    """Read a record."""
    if DB_NAME == 'mongo':
        if c_id is None:
            return coll.find()
        else:
            return coll.find_one(dict(id=c_id))
    else:
        raise NotImplemented('PostgreSQL is not yet supported.')


def update(c_id, data=None, fmt_modules=True):
    """Update a record."""
    if data is None:
        return
    if DB_NAME == 'mongo':
        modules = _format_modules(data) if fmt_modules else data.get('modules')
        save_conf = {
            '$set': {
                'name': data['name'],
                'modules': modules,
                'date': dt.now()
            }
        }
        coll.update(dict(id=c_id), save_conf)
    else:
        raise NotImplemented('PostgreSQL is not yet supported.')


def create(data=None):
    """Add a new record."""
    if data is None:
        return
    if DB_NAME == 'mongo':
        coll.insert(data)
    else:
        raise NotImplemented('PostgreSQL is not yet supported.')


def delete(c_id):
    """Delete a record."""
    if DB_NAME == 'mongo':
        coll.delete_one(dict(id=c_id))
    else:
        raise NotImplemented('PostgreSQL is not yet supported.')
