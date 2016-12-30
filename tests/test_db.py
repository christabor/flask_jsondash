import json

import pytest

from flask_jsondash import db
from flask_jsondash import settings
from flask_jsondash import mongo_adapter


def test_reformat_data():
    c_id = 3
    res = db.reformat_data(dict(), c_id)
    assert isinstance(res, dict)
    assert 'date' in res
    assert res.get('id') == c_id


def test_format_charts():
    data = {'module_': json.dumps(dict()), 'name': 'foo'}
    res = db.format_charts(data)
    assert isinstance(res, list)
    assert res != []
    assert len(res) == 1


def test_format_charts_invalid():
    data = {'Foo': json.dumps(dict())}
    res = db.format_charts(data)
    assert res == []


def test_default_dbname():
    assert db.DB_NAME == 'mongo'


def test_default_settings():
    assert settings.DB_URI == 'localhost'
    assert settings.DB_PORT == 27017
    assert settings.DB_NAME == 'charts'
    assert settings.DB_TABLE == 'views'
    assert settings.ACTIVE_DB == 'mongo'
    assert db.DB_NAME == settings.ACTIVE_DB


def test_get_db_handler_mongo():
    assert isinstance(db.get_db_handler(), mongo_adapter.Db)


def test_get_db_handler_invalid(monkeypatch):
    monkeypatch.setattr(db, 'DB_NAME', 'invaliddb')
    with pytest.raises(NotImplementedError):
        db.get_db_handler()
