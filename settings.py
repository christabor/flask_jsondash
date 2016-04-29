"""App/blueprint wide settings."""

import os

DB_URI = os.environ.get('CHARTS_DB_HOST', 'localhost')
DB_PORT = os.environ.get('CHARTS_DB_PORT', 27017)
DB_NAME = os.environ.get('CHARTS_DB_DB', 'charts')
# This name is used for table/collection,
# regardless of Postgresql or Mongodb usage.
DB_TABLE = os.environ.get('CHARTS_DB_TABLE', 'views')
ACTIVE_DB = os.environ.get('CHARTS_ACTIVE_DB', 'mongo').lower()
