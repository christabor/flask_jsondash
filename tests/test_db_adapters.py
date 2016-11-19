import json
from datetime import datetime as dt

from flask_jsondash import db_adapters
from flask_jsondash import settings


def test_reformat_data():
    c_id = 3
    res = db_adapters.reformat_data(dict(), c_id)
    assert isinstance(res, dict)
    assert 'date' in res
    assert res.get('id') == c_id


def test_format_modules():
    data = {'module_': json.dumps(dict()), 'name': 'foo'}
    res = db_adapters._format_modules(data)
    assert isinstance(res, list)
    assert res != []
    assert len(res) == 1


def test_format_modules_invalid():
    data = {'Foo': json.dumps(dict())}
    res = db_adapters._format_modules(data)
    assert res == []


def test_create_none():
    assert db_adapters.create() is None


def test_default_dbname():
    assert db_adapters.DB_NAME == 'mongo'


def test_default_settings():
    assert settings.DB_URI == 'localhost'
    assert settings.DB_PORT == 27017
    assert settings.DB_NAME == 'charts'
    assert settings.DB_TABLE == 'views'
    assert settings.ACTIVE_DB == 'mongo'
