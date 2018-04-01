from pyquery import PyQuery as pq

import pytest

from tests.conftest import auth_invalid

from flask_jsondash import charts_builder


@pytest.mark.auth
def test_auth_no_appconfig(ctx, client):
    app, test = client
    del app.config['JSONDASH']
    assert charts_builder.auth()


@pytest.mark.auth
def test_auth_no_authconfig(ctx, client):
    app, test = client
    del app.config['JSONDASH']['auth']
    assert charts_builder.auth()


@pytest.mark.auth
def test_auth_false_realauth(ctx, client):
    app, test = client
    assert not charts_builder.auth(authtype='create')
    assert not charts_builder.auth(authtype='view')
    assert not charts_builder.auth(authtype='delete')
    assert not charts_builder.auth(authtype='clone')
    assert not charts_builder.auth(authtype='edit_global')
    assert not charts_builder.auth(authtype='edit_others')


@pytest.mark.auth
def test_no_auth_view(ctx, client, monkeypatch):
    app, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_invalid)
    res = str(test.get('/charts/foo', follow_redirects=True).data)
    alerts = pq(res).find('.alert-danger').text()
    assert 'You do not have access to view this dashboard.' in alerts


@pytest.mark.auth
def test_no_auth_delete(ctx, client, monkeypatch):
    app, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_invalid)
    res = str(test.post('/charts/foo/delete',
              data=dict(), follow_redirects=True).data)
    alerts = pq(res).find('.alert-danger').text()
    assert 'You do not have access to delete dashboards.' in alerts


@pytest.mark.auth
def test_no_auth_update(ctx, client, monkeypatch):
    app, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_invalid)
    res = str(test.post('/charts/foo/update',
              data=dict(), follow_redirects=True).data)
    alerts = pq(res).find('.alert-danger').text()
    assert 'You do not have access to update dashboards.' in alerts


@pytest.mark.auth
def test_no_auth_create(ctx, client, monkeypatch):
    app, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_invalid)
    res = str(test.post('/charts/create',
              data=dict(), follow_redirects=True).data)
    alerts = pq(res).find('.alert-danger').text()
    assert 'You do not have access to create dashboards.' in alerts


@pytest.mark.auth
def test_no_auth_clone(ctx, client, monkeypatch):
    app, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_invalid)
    res = str(test.post('/charts/foo/clone', follow_redirects=True).data)
    alerts = pq(res).find('.alert-danger').text()
    assert 'You do not have access to clone dashboards.' in alerts


@pytest.mark.auth
def test_auth_true_realauth(ctx, client):
    app, test = client

    def authfunc(*args):
        return True

    app.config['JSONDASH']['auth'] = dict(
        clone=authfunc,
        edit_global=authfunc,
        create=authfunc,
        delete=authfunc,
        view=authfunc,
    )
    assert charts_builder.auth(authtype='create')
    assert charts_builder.auth(authtype='view')
    assert charts_builder.auth(authtype='delete')
    assert charts_builder.auth(authtype='clone')
    assert charts_builder.auth(authtype='edit_global')
    assert charts_builder.auth(authtype='edit_others')
