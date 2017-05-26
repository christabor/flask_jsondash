import json

from conftest import setup_dashboard


def test_grid_mode_has_no_cols_empty_single_row(monkeypatch, ctx, client):
    app, test = client
    data = dict(
        mode='grid',
        name='Some dashboard',
    )
    dom = setup_dashboard(monkeypatch, app, test, data)
    container = dom.find('#container')
    assert len(container.find('.grid-row')) == 0
    # Test it has 2 add row buttons - top and bottom
    assert len(container.find('.add-new-row-container')) == 2


def test_grid_mode_has_2_rows(monkeypatch, ctx, client):
    app, test = client
    data = dict(
        mode='grid',
        name='Some dashboard',
        module_foo=json.dumps(
            dict(name=1, width=1, height=1, dataSource='...', row=2)
        ),
        module_bar=json.dumps(
            dict(name=1, width=1, height=1, dataSource='...', row=1),
        ),
    )
    dom = setup_dashboard(monkeypatch, app, test, data)
    container = dom.find('#container')
    assert len(container.find('.grid-row')) == 2


def test_grid_mode_has_correct_cols(monkeypatch, ctx, client):
    app, test = client
    data = dict(
        mode='grid',
        name='Some dashboard',
        module_foo=json.dumps(
            dict(name=1, width='col-4', height=1, dataSource='...', row=2)
        ),
        module_bar=json.dumps(
            dict(name=1, width='col-4', height=1, dataSource='...', row=1),
        ),
    )
    dom = setup_dashboard(monkeypatch, app, test, data)
    container = dom.find('#container')
    assert len(container.find('.grid-row')) == 2
    assert len(container.find('.col-md-4')) == 2


def test_grid_mode_correct_multicols_multirows(monkeypatch, ctx, client):
    app, test = client
    data = dict(
        mode='grid',
        name='Some dashboard - lots of cols and rows',
        module_baz=json.dumps(
            dict(name=1, width='col-12', height=1, dataSource='...', row=1)
        ),
        module_foo=json.dumps(
            dict(name=1, width='col-5', height=1, dataSource='...', row=2)
        ),
        module_bar=json.dumps(
            dict(name=1, width='col-4', height=1, dataSource='...', row=2),
        ),
        module_quux=json.dumps(
            dict(name=1, width='col-3', height=1, dataSource='...', row=2),
        ),
        module_quux2=json.dumps(
            dict(name=1, width='col-6', height=1, dataSource='...', row=3),
        ),
        module_quux3=json.dumps(
            dict(name=1, width='col-6', height=1, dataSource='...', row=3),
        ),
    )
    dom = setup_dashboard(monkeypatch, app, test, data)
    container = dom.find('#container')
    assert len(container.find('.grid-row')) == 3
    assert len(container.find('.grid-row').find('.col-md-6')) == 2
    assert len(container.find('.grid-row').find('.col-md-12')) == 1
    assert len(container.find('.grid-row').find('.col-md-5')) == 1
    assert len(container.find('.grid-row').find('.col-md-4')) == 1
    assert len(container.find('.grid-row').find('.col-md-3')) == 1
