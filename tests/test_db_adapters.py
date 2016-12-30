import json
from datetime import datetime

from pymongo.cursor import Cursor as MongoCursor

from flask_jsondash import db_adapters
from flask_jsondash import settings


def test_reformat_data():
    c_id = 3
    res = db_adapters.reformat_data(dict(), c_id)
    assert isinstance(res, dict)
    assert 'date' in res
    assert res.get('id') == c_id


def test_format_charts():
    data = {'module_': json.dumps(dict()), 'name': 'foo'}
    res = db_adapters.format_charts(data)
    assert isinstance(res, list)
    assert res != []
    assert len(res) == 1


def test_format_charts_invalid():
    data = {'Foo': json.dumps(dict())}
    res = db_adapters.format_charts(data)
    assert res == []


def test_create(monkeypatch):
    monkeypatch.setattr(
        db_adapters.coll, 'insert', lambda *args, **kwargs: kwargs)
    assert db_adapters.create(data=dict(foo='bar')) is None


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
    assert db_adapters.DB_NAME == settings.ACTIVE_DB


def test_update_normal(monkeypatch):
    records = []
    monkeypatch.setattr(
        db_adapters.coll, 'update',
        lambda *args, **kwargs: records.append(args))
    db_adapters.update('foo-id', data=dict(name='foo'))
    assert records[0][0]['id'] == 'foo-id'
    assert records[0][1]['$set']['name'] == 'foo'
    assert records[0][1]['$set']['modules'] == []
    assert isinstance(records[0][1]['$set']['date'], datetime)


def test_update_format_charts(monkeypatch):
    records = []
    monkeypatch.setattr(
        db_adapters.coll, 'update',
        lambda *args, **kwargs: records.append(args))
    data = {
        'module_1': json.dumps(dict(name='chart-1')),
        'module_2': json.dumps(dict(name='chart-2')),
        'name': 'foo'
    }
    db_adapters.update('foo-id', data=data)
    assert records[0][0]['id'] == 'foo-id'
    assert records[0][1]['$set']['name'] == 'foo'
    assert len(records[0][1]['$set']['modules']) == 2
    assert 'module_1' in records[0][1]['$set'].keys()
    assert 'module_2' in records[0][1]['$set'].keys()
    assert isinstance(records[0][1]['$set']['date'], datetime)


def test_update_nothing(monkeypatch):
    monkeypatch.setattr(
        db_adapters.coll, 'update', lambda *args, **kwargs: kwargs)
    assert db_adapters.update('foobar') is None


def test_read_one(monkeypatch):
    records = [dict()]
    monkeypatch.setattr(
        db_adapters.coll, 'find_one', lambda *args, **kwargs: records)
    assert db_adapters.read(c_id='foo') == records


def test_read_all(monkeypatch):
    assert isinstance(db_adapters.read(), MongoCursor)


def test_delete_one(monkeypatch):
    monkeypatch.setattr(
        db_adapters.coll, 'delete_one', lambda *args, **kwargs: kwargs)
    assert db_adapters.delete(c_id='foo') is None


def test_delete_all(monkeypatch):
    monkeypatch.setattr(
        db_adapters.coll, 'remove', lambda *args, **kwargs: kwargs)
    assert db_adapters.delete_all() is None
