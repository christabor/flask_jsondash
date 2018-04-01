import os
import json

from click.testing import CliRunner

from flask_jsondash import model_factories
from flask_jsondash.settings import CHARTS_CONFIG
from tests.conftest import read

_db = model_factories.adapter


def test_get_random_group():
    conf_vals = CHARTS_CONFIG.values()
    data = model_factories.get_random_group()
    assert isinstance(data, dict)
    assert 'charts' in data
    assert data in conf_vals


def test_get_random_chart():
    chart = model_factories.get_random_group()
    data = model_factories.get_random_chart(chart)
    assert isinstance(data, tuple)


def test_make_fake_dashboard():
    fdash = model_factories.make_fake_dashboard(name='Foo', max_charts=4)
    assert isinstance(fdash, dict)
    assert fdash.get('name') == 'Foo'


def test_make_fake_chart_data():
    chartdata = model_factories.make_fake_chart_data(name='Foo')
    chartconfig = json.loads(chartdata[1])
    assert isinstance(chartdata, tuple)
    assert isinstance(chartconfig, dict)
    assert chartconfig.get('name') == 'Foo'


def test_insert_dashboards(monkeypatch):
    records = []
    runner = CliRunner()
    args = ['--max-charts', 5, '--records', 5]
    monkeypatch.setattr(_db, 'create', lambda *a, **kw: records.append(a))
    result = runner.invoke(model_factories.insert_dashboards, args)
    assert result.exit_code == 0
    assert len(records) == 5


def test_delete_all(monkeypatch):
    monkeypatch.setattr(_db, 'delete_all', lambda *a, **kw: [])
    assert model_factories.delete_all() is None


def test_load_fixtures(monkeypatch):
    records = []
    runner = CliRunner()
    args = ['--fixtures', 'example_app/examples/config']
    monkeypatch.setattr(_db, 'create', lambda *a, **kw: records.append(a))
    result = runner.invoke(model_factories.insert_dashboards, args)
    assert result.exit_code == 0
    assert len(records) == 19  # Changed as new examples are added.


def test_dump_fixtures_empty(monkeypatch, tmpdir):
    records = []
    monkeypatch.setattr(_db, 'read', lambda *args, **kwargs: records)
    runner = CliRunner()
    tmp = tmpdir.mkdir('dumped_fixtures_test')
    args = ['--dump', tmp.strpath]
    result = runner.invoke(model_factories.insert_dashboards, args)
    assert 'Nothing to dump.' in result.output
    assert result.exit_code == 0
    assert len(os.listdir(tmp.strpath)) == len(records)


def test_dump_fixtures(monkeypatch, tmpdir):
    records = [
        model_factories.make_fake_dashboard(name=i, max_charts=1)
        for i in range(10)]
    # Also ensure _id is popped off.
    for r in records:
        r.update(_id='foo')
    monkeypatch.setattr(_db, 'read', lambda *args, **kwargs: records)
    runner = CliRunner()
    tmp = tmpdir.mkdir('dumped_fixtures_test')
    args = ['--dump', tmp.strpath]
    result = runner.invoke(model_factories.insert_dashboards, args)
    assert 'Saving db as fixtures to:' in result.output
    assert result.exit_code == 0
    assert len(os.listdir(tmp.strpath)) == len(records)


def test_dump_fixtures_delete(monkeypatch, tmpdir):
    records = [
        model_factories.make_fake_dashboard(name=i, max_charts=1)
        for i in range(10)]

    def delete_all():
        global records
        records = []

    monkeypatch.setattr(_db, 'read', lambda *args, **kwargs: records)
    monkeypatch.setattr(_db, 'delete_all', lambda *a, **kw: [])
    runner = CliRunner()
    tmp = tmpdir.mkdir('dumped_fixtures_test')
    args = ['--dump', tmp.strpath, '--delete']
    result = runner.invoke(model_factories.insert_dashboards, args)
    assert 'Saving db as fixtures to:' in result.output
    assert result.exit_code == 0
    assert len(os.listdir(tmp.strpath)) == 10
    assert len(read()) == 0


def test_dump_fixtures_delete_bad_path_show_errors_no_exception(monkeypatch):
    records = [
        model_factories.make_fake_dashboard(name=i, max_charts=1)
        for i in range(1)]

    def delete_all():
        global records
        records = []

    monkeypatch.setattr(_db, 'read', lambda *args, **kwargs: records)
    monkeypatch.setattr(_db, 'delete_all', lambda *a, **kw: [])
    runner = CliRunner()
    args = ['--dump', '/fakepath/', '--delete']
    result = runner.invoke(model_factories.insert_dashboards, args)
    assert 'Saving db as fixtures to:' in result.output
    assert result.exit_code == 0
    assert len(read()) == 0
    err_msg = "The following records could not be dumped: ['//fakepath/"
    assert err_msg in result.output


def test_delete_all_cli(monkeypatch):
    runner = CliRunner()
    args = ['--delete']
    monkeypatch.setattr(_db, 'delete_all', lambda *a, **kw: [])
    assert model_factories.delete_all() is None
    result = runner.invoke(model_factories.insert_dashboards, args)
    assert 'Deleting all records!' in result.output
    assert result.exit_code == 0
