import json
from datetime import datetime as dt

from flask import (
    Flask,
    current_app,
    url_for,
)
import pytest

from flask_jsondash import charts_builder

URL_BASE = 'http://127.0.0.1:80'
app = Flask('test_flask_jsondash',
            template_folder='../flask_jsondash/example_app/templates')
app.config.update(
    # Required to fix context errors.
    # See https://github.com/jarus/flask-testing/issues/21
    PRESERVE_CONTEXT_ON_EXCEPTION=False,
    SECRET_KEY='123',
)
app.debug = True
app.register_blueprint(charts_builder.charts)

fake_db = []

def _username():
    return 'Username'


def auth_ok(**kwargs):
    return True


def _authtest(**kwargs):
    return False


def read(*args, **kwargs):
    if 'override' in kwargs:
        newkwargs = kwargs.pop('override')
        def _read(*args, **kwargs):
            return dict(**newkwargs)
        return _read
    if 'c_id' not in kwargs:
        return fake_db
    for i, dash in enumerate(fake_db):
        if dash['id'] == kwargs.get('c_id'):
            return dash


def delete(c_id, **kwargs):
    global fake_db
    for i, dash in enumerate(fake_db):
        if dash['id'] == c_id:
            del fake_db[i]
            break


def create(*args, **kwargs):
    global fake_db
    fake_db.append(dict(**kwargs.get('data')))


def update(c_id, **kwargs):
    global fake_db
    for i, dash in enumerate(fake_db):
        if dash['id'] == c_id:
            fake_db[i].update(**kwargs)
            break


@pytest.fixture()
def ctx(monkeypatch, request):
    with app.test_request_context() as req_ctx:
        global fake_db
        fake_db = []
        monkeypatch.setattr(charts_builder.adapter, 'read', read)
        monkeypatch.setattr(charts_builder.adapter, 'create', create)
        monkeypatch.setattr(charts_builder.adapter, 'delete', delete)
        monkeypatch.setattr(charts_builder.adapter, 'update', update)
        yield req_ctx


@pytest.fixture()
def client():
    app.config.update(
        JSONDASH_GLOBALDASH=False,
        JSONDASH_FILTERUSERS=False,
        JSONDASH_GLOBAL_USER='global-test',
    )
    app.config['JSONDASH'] = dict(
        metadata=dict(
            created_by=_username,
            username=_username,
        ),
        static=dict(
            js_path='js/vendor/',
            css_path='css/vendor/',
        ),
        auth=dict(
            edit_others=_authtest,
            edit_global=_authtest,
            create=_authtest,
            view=_authtest,
            clone=_authtest,
            delete=_authtest,
        )
    )
    return app, app.test_client()
