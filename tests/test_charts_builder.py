import json
from datetime import datetime as dt

from flask import (
    Flask,
    current_app,
    url_for,
)
import pytest
from conftest import URL_BASE

from flask_jsondash import charts_builder


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
    assert charts_builder.is_global_dashboard(
        dict(created_by='global-test'))


@pytest.mark.globalflag
def test_is_global_dashboard_false(ctx, client):
    app, test = client
    is_global = charts_builder.is_global_dashboard
    assert not is_global(dict(created_by='foo'))
    assert not is_global(dict(created_by='Username'))


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


@pytest.mark.auth
def test_auth_true_fakeauth(ctx, client):
    app, test = client
    assert charts_builder.auth(authtype=None)
    assert charts_builder.auth(authtype='foo')
    assert charts_builder.metadata(key='foo') is None


def test_metadata(ctx, client):
    app, test = client
    assert charts_builder.metadata() == dict(
        username='Username',
        created_by='Username',
    )
    assert charts_builder.metadata(key='username') == 'Username'
    assert charts_builder.metadata(key='created_by') == 'Username'
    assert charts_builder.metadata(exclude='created_by') == dict(
        username='Username'
    )
    assert charts_builder.metadata(exclude='username') == dict(
        created_by='Username'
    )


@pytest.mark.filters
def test_getdims_normal(ctx, client):
    app, test = client
    data = dict(width=100, height=100, type='foo')
    expected = dict(width=100, height=100)
    assert charts_builder.get_dims(object, data) == expected


@pytest.mark.filters
def test_getdims_youtube(ctx, client):
    app, test = client
    yt = ('<iframe width="650" height="366" '
          'src="https://www.youtube.com/embed/'
          '_hI0qMtdfng?list=RD_hI0qMtdfng&amp;'
          'controls=0&amp;showinfo=0" frameborder="0"'
          ' allowfullscreen></iframe>')
    data = dict(type='youtube', dataSource=yt, width=100, height=100)
    expected = dict(width=650 + 20, height=366 + 60)
    assert charts_builder.get_dims(object, data) == expected


@pytest.mark.filters
def test_jsonstring(ctx, client):
    app, test = client
    now = dt.now()
    data = dict(date=now, foo='bar')
    res = charts_builder.jsonstring(object, data)
    assert 'foo' in res
    assert isinstance(res, str)
    d = json.loads(res)
    assert isinstance(d['date'], unicode)


@pytest.mark.utils
def test_order_sort():
    item = dict()
    assert charts_builder.order_sort(item) == item
    item = dict(order=1)
    assert charts_builder.order_sort(item) == 1


def test_app_redirects(ctx, client):
    app, test = client
    res = test.get('/charts')
    assert 'You should be redirected automatically' in res.data


def test_routes(ctx, client):
    app, test = client
    app.config['SERVER_NAME'] = '127.0.0.1:80'
    app, test = client
    assert url_for('jsondash.dashboard') == '/charts/'
    assert url_for('jsondash.view', c_id='foo') == '/charts/foo'
    assert url_for('jsondash.update', c_id='foo') == '/charts/foo/update'
    assert url_for('jsondash.clone', c_id='foo') == '/charts/foo/clone'
    assert url_for('jsondash.delete', c_id='foo') == '/charts/foo/delete'
    assert url_for('jsondash.create') == '/charts/create'
