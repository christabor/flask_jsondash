import json
from datetime import datetime as dt

from flask import Flask
import pytest

from flask_jsondash import charts_builder


app = Flask('test_flask_jsondash')
app.debug = True
app.register_blueprint(charts_builder.charts)


@pytest.fixture
def client(request):
    app.config.update(
        JSONDASH_GLOBALDASH=False,
        JSONDASH_FILTERUSERS=False,
        JSONDASH_GLOBAL_USER='global-test',
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
