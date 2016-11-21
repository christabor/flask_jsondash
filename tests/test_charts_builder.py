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


def test_no_config_sanity_test(client):
    app, test = client
    assert not app.config.get('JSONDASH_GLOBALDASH')
    assert not app.config.get('JSONDASH_FILTERUSERS')
    assert app.config.get('JSONDASH_GLOBAL_USER') == 'global-test'


def test_setting(client):
    app, test = client
    with app.app_context():
        _get = charts_builder.setting
        assert not _get('JSONDASH_GLOBALDASH')
        assert not _get('JSONDASH_FILTERUSERS')
        assert _get('JSONDASH_GLOBAL_USER') == 'global-test'


def test_is_global_dashboard_true(client):
    app, test = client
    with app.app_context():
        app.config.update(JSONDASH_GLOBALDASH=True)
        assert charts_builder.is_global_dashboard(
            dict(created_by='global-test'))


def test_is_global_dashboard_false(client):
    app, test = client
    with app.app_context():
        is_global = charts_builder.is_global_dashboard
        assert not is_global(dict(created_by='foo'))
        assert not is_global(dict(created_by='Username'))


def test_auth_false_realauth(client):
    app, test = client
    with app.app_context():
        assert not charts_builder.auth(authtype='create')
        assert not charts_builder.auth(authtype='view')
        assert not charts_builder.auth(authtype='delete')
        assert not charts_builder.auth(authtype='clone')
        assert not charts_builder.auth(authtype='edit_global')
        assert not charts_builder.auth(authtype='edit_others')


def test_auth_true_realauth(client):
    app, test = client
    with app.app_context():
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


def test_auth_true_fakeauth(client):
    app, test = client
    with app.app_context():
        assert charts_builder.auth(authtype=None)
        assert charts_builder.auth(authtype='foo')
        assert charts_builder.metadata(key='foo') is None


def test_metadata(client):
    app, test = client
    with app.app_context():
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
def test_getdims_normal(client):
    app, test = client
    with app.app_context():
        data = dict(width=100, height=100, type='foo')
        expected = dict(width=100, height=100)
        assert charts_builder.get_dims(object, data) == expected


@pytest.mark.filters
def test_getdims_youtube(client):
    app, test = client
    with app.app_context():
        yt = ('<iframe width="650" height="366" '
              'src="https://www.youtube.com/embed/'
              '_hI0qMtdfng?list=RD_hI0qMtdfng&amp;'
              'controls=0&amp;showinfo=0" frameborder="0"'
              ' allowfullscreen></iframe>')
        data = dict(type='youtube', dataSource=yt, width=100, height=100)
        expected = dict(width=650 + 20, height=366 + 60)
        assert charts_builder.get_dims(object, data) == expected


@pytest.mark.filters
def test_jsonstring(client):
    app, test = client
    with app.app_context():
        now = dt.now()
        data = dict(date=now, foo='bar')
        res = charts_builder.jsonstring(object, data)
        assert 'foo' in res
        assert isinstance(res, str)
        d = json.loads(res)
        assert isinstance(d['date'], unicode)


def test_app_redirects(client):
    app, test = client
    with app.app_context():
        res = test.get('/charts')
        assert 'You should be redirected automatically' in res.data


def test_routes(client):
    app, test = client
    app.config['SERVER_NAME'] = '127.0.0.1:80'
    app, test = client
    with app.app_context():
        # Index
        url = '{}/charts/'.format(URL_BASE)
        assert url_for('jsondash.dashboard') == url
        # View
        url = '{}/charts/foo'.format(URL_BASE)
        assert url_for('jsondash.view', c_id='foo') == url
        # Update
        url = '{}/charts/foo/update'.format(URL_BASE)
        assert url_for('jsondash.update', c_id='foo') == url
        # Clone
        url = '{}/charts/foo/clone'.format(URL_BASE)
        assert url_for('jsondash.clone', c_id='foo') == url
        # Delete
        url = '{}/charts/foo/delete'.format(URL_BASE)
        assert url_for('jsondash.delete', c_id='foo') == url
        # Create
        url = '{}/charts/create'.format(URL_BASE)
        assert url_for('jsondash.create') == url
