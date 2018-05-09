import json

from datetime import datetime

from pymongo.cursor import Cursor as MongoCursor


def test_create(monkeypatch, adapter):
    monkeypatch.setattr(adapter.coll, 'insert', lambda *args, **kwargs: kwargs)
    assert adapter.create(data=dict(foo='bar')) is None


def test_create_none(adapter):
    assert adapter.create() is None


def test_count(monkeypatch, adapter):
    monkeypatch.setattr(adapter.coll, 'count', lambda *args, **kwargs: [])
    assert adapter.count() == []


def test_update_normal(monkeypatch, adapter):
    records = []
    monkeypatch.setattr(
        adapter.coll, 'update', lambda *args, **kwargs: records.append(args))
    adapter.update('foo-id', data=dict(name='foo'))
    assert records[0][0]['id'] == 'foo-id'
    assert records[0][1]['$set']['name'] == 'foo'
    assert records[0][1]['$set']['modules'] == []
    assert isinstance(records[0][1]['$set']['date'], datetime)


def test_update_format_charts(monkeypatch, adapter):
    records = []
    monkeypatch.setattr(
        adapter.coll, 'update', lambda *args, **kwargs: records.append(args))
    data = {
        'module_1': json.dumps(dict(name='chart-1')),
        'module_2': json.dumps(dict(name='chart-2')),
        'name': 'foo'
    }
    adapter.update('foo-id', data=data)
    assert records[0][0]['id'] == 'foo-id'
    assert records[0][1]['$set']['name'] == 'foo'
    assert len(records[0][1]['$set']['modules']) == 2
    assert 'module_1' in list(records[0][1]['$set'].keys())
    assert 'module_2' in list(records[0][1]['$set'].keys())
    assert isinstance(records[0][1]['$set']['date'], datetime)


def test_update_nothing(monkeypatch, adapter):
    monkeypatch.setattr(adapter.coll, 'update', lambda *args, **kwargs: kwargs)
    assert adapter.update('foobar') is None


def test_read_one(monkeypatch, adapter):
    records = [dict()]
    monkeypatch.setattr(
        adapter.coll, 'find_one', lambda *args, **kwargs: records)
    assert adapter.read(c_id='foo') == records


def test_read_all(monkeypatch, adapter):
    assert isinstance(adapter.read(), MongoCursor)


def test_delete_one(monkeypatch, adapter):
    monkeypatch.setattr(
        adapter.coll, 'delete_one', lambda *args, **kwargs: kwargs)
    assert adapter.delete(c_id='foo') is None


def test_delete_all(monkeypatch, adapter):
    monkeypatch.setattr(adapter.coll, 'remove', lambda *args, **kwargs: kwargs)
    assert adapter.delete_all() is None
