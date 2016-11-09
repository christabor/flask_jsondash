import json
from datetime import datetime as dt

from flask import Flask
import pytest

from flask_jsondash import charts_builder


app = Flask('test_flask_jsondash')
app.debug = True
app.register_blueprint(charts_builder.charts)


def _username():
    return 'Username'


def _authtest():
    return False


@pytest.fixture
def client(request):
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
            edit_global=_authtest,
            clone=_authtest,
            delete=_authtest,
        )
    )
    return app.test_client()


def test_no_config_sanity_test(client):
    assert app.config.get('JSONDASH_GLOBALDASH') == False
    assert app.config.get('JSONDASH_FILTERUSERS') == False
    assert app.config.get('JSONDASH_GLOBAL_USER') == 'global-test'


def test_setting(client):
    with app.app_context():
        _get = charts_builder.setting
        assert _get('JSONDASH_GLOBALDASH') == False
        assert _get('JSONDASH_FILTERUSERS') == False
        assert _get('JSONDASH_GLOBAL_USER') == 'global-test'


def test_metadata(client):
    with app.app_context():
        assert charts_builder.metadata(key='created_by') == 'Username'
        assert charts_builder.metadata(key='username') == 'Username'
