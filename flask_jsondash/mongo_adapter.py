# -*- coding: utf-8 -*-

"""
flask_jsondash.mongo_adapter
~~~~~~~~~~~~~~~~~~~~~~~~~~

Adapters for various storage engines.
"""

from datetime import datetime as dt


class Db(object):
    """Adapter for all mongo operations."""

    def __init__(self, client, conn, coll, formatter):
        """Setup connection."""
        self.client = client
        self.conn = conn
        self.coll = coll
        self.formatter = formatter

    def count(self, **kwargs):
        """Standard db count."""
        return self.coll.count(**kwargs)

    def read(self, **kwargs):
        """Read a record."""
        if kwargs.get('c_id') is None:
            return self.coll.find(**kwargs)
        else:
            return self.coll.find_one(dict(id=kwargs.pop('c_id')))

    def update(self, c_id, data=None, fmt_charts=True):
        """Update a record."""
        if data is None:
            return
        charts = self.formatter(data) if fmt_charts else data.get('modules')
        save_conf = {
            '$set': {
                'name': data.get('name', 'NONAME'),
                'modules': charts,
                'date': dt.now()
            }
        }
        save_conf['$set'].update(**data)
        self.coll.update(dict(id=c_id), save_conf)

    def create(self, data=None):
        """Add a new record."""
        if data is None:
            return
        self.coll.insert(data)

    def delete(self, c_id):
        """Delete a record."""
        self.coll.delete_one(dict(id=c_id))

    def delete_all(self):
        """Delete ALL records. Separated function for safety.

        This should never be used for production.
        """
        self.coll.remove()
