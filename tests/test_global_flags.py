import pytest

from pyquery import PyQuery as pq

from flask_jsondash import charts_builder

from flask_jsondash import utils

from tests.conftest import (
    auth_valid,
    read,
)


@pytest.mark.globalflag
def test_noset_global_flag_when_creating_dashboard(ctx, client, monkeypatch):
    app, test = client
    app.config['JSONDASH_GLOBALDASH'] = True
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    data = dict(name='global-check')
    test.post('/charts/create', data=data).data
    assert len(read()) == 1
    assert read()[0]['name'] == 'global-check'
    assert read()[0]['created_by'] == 'Username'


@pytest.mark.globalflag
def test_set_global_flag_when_creating_dashboard(ctx, client, monkeypatch):
    app, test = client
    app.config['JSONDASH_GLOBALDASH'] = True
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    data = dict(name='global-check', is_global='on')
    test.post('/charts/create', data=data).data
    assert len(read()) == 1
    assert read()[0]['name'] == 'global-check'
    assert read()[0]['created_by'] == app.config.get('JSONDASH_GLOBAL_USER')


@pytest.mark.globalflag
def test_no_config_sanity_test(ctx, client):
    app, test = client
    assert not app.config.get('JSONDASH_GLOBALDASH')
    assert not app.config.get('JSONDASH_FILTERUSERS')
    assert app.config.get('JSONDASH_GLOBAL_USER') == 'global-test'


@pytest.mark.globalflag
def test_setting(ctx, client):
    app, test = client
    _get = charts_builder.setting
    assert not _get('JSONDASH_GLOBALDASH')
    assert not _get('JSONDASH_FILTERUSERS')
    assert _get('JSONDASH_GLOBAL_USER') == 'global-test'


@pytest.mark.globalflag
def test_is_global_dashboard_true(ctx, client):
    app, test = client
    app.config.update(JSONDASH_GLOBALDASH=True)
    # assert charts_builder.is_global_dashboard(
    assert utils.is_global_dashboard(
        dict(created_by='global-test'))


@pytest.mark.globalflag
def test_is_global_dashboard_false(ctx, client):
    app, test = client
    is_global = utils.is_global_dashboard
    assert not is_global(dict(created_by='foo'))
    assert not is_global(dict(created_by='Username'))


@pytest.mark.globalflag
def test_dashboard_filter_users_and_all_global(ctx, client, monkeypatch):
    app, test = client
    app.config['JSONDASH_FILTERUSERS'] = True
    app.config['JSONDASH_GLOBALDASH'] = True
    assert charts_builder.setting('JSONDASH_FILTERUSERS')
    assert charts_builder.setting('JSONDASH_GLOBALDASH')
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    data = dict(name='global-check')
    test.post('/charts/create', data=data).data
    res = test.get('/charts', follow_redirects=True).data
    dom = pq(res)
    text = dom.find('p > small').text()
    assert 'Only showing' in text
    assert 'and all global dashboards' in text
    assert 'Not filtering any dashboards.' not in text
