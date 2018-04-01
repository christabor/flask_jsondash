import json

from tests.conftest import setup_dashboard


def test_freeform_mode_has_no_rows_or_cols(monkeypatch, ctx, client):
    app, test = client
    data = dict(
        mode='freeform',
        name='Some dashboard',
        module_baz=json.dumps(
            dict(name=1, width=400, height=112, dataSource='...')
        ),
        module_foo=json.dumps(
            dict(name=1, width=300, height=112, dataSource='...')
        ),
    )
    dom = setup_dashboard(monkeypatch, app, test, data)
    container = dom.find('#container')
    assert len(container.find('.grid-row')) == 0
