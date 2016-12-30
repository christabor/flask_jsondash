import json
from datetime import datetime as dt
from random import shuffle

from flask import url_for

from pyquery import PyQuery as pq

import pytest

from conftest import (
    get_json_config,
    auth_valid,
    read,
)

from flask_jsondash import charts_builder
from flask_jsondash import settings

REDIRECT_MSG = 'You should be redirected automatically'


# Py2/3 compat.
try:
    _unicode = unicode
except NameError:
    _unicode = str


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
    assert charts_builder.is_global_dashboard(
        dict(created_by='global-test'))


@pytest.mark.globalflag
def test_is_global_dashboard_false(ctx, client):
    app, test = client
    is_global = charts_builder.is_global_dashboard
    assert not is_global(dict(created_by='foo'))
    assert not is_global(dict(created_by='Username'))


@pytest.mark.auth
@pytest.mark.metadata
def test_auth_true_fakeauth(ctx, client):
    app, test = client
    assert charts_builder.auth(authtype=None)
    assert charts_builder.auth(authtype='foo')
    assert charts_builder.metadata(key='foo') is None


@pytest.mark.metadata
def test_metadata(ctx, client):
    app, test = client
    assert charts_builder.metadata() == dict(
        username='Username',
        created_by='Username',
    )
    assert charts_builder.metadata(key='username') == 'Username'
    assert charts_builder.metadata(key='created_by') == 'Username'


@pytest.mark.metadata
def test_metadata_exclude(ctx, client):
    app, test = client
    assert charts_builder.metadata() == dict(
        username='Username',
        created_by='Username',
    )
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
    assert isinstance(d['date'], _unicode)


@pytest.mark.utils
def test_order_sort_force_valueerror():
    item = dict(order='NaN')
    assert charts_builder.order_sort(item) == -1


@pytest.mark.utils
def test_order_sort_invalid_key():
    item = dict()
    assert charts_builder.order_sort(item) == -1


@pytest.mark.utils
def test_order_sort_valid_key():
    item = dict(order=1)
    assert charts_builder.order_sort(item) == 1


@pytest.mark.utils
def test_order_shuffled_sort_multiple_valid_key():
    orders = list(range(0, 10))
    shuffle(orders)
    modules = [dict(order=i, foo='bar') for i in orders]
    res = sorted(modules, key=charts_builder.order_sort)
    for i in range(0, 10):
        assert res[i]['order'] == i


@pytest.mark.utils
def test_order_shuffled_sort_multiple_valid_key_one_invalid_key():
    orders = list(range(0, 10))
    shuffle(orders)
    modules = [dict(order=i, foo='bar') for i in orders]
    # Add one w/o order key.
    modules.append(dict(foo='bar'))
    res = sorted(modules, key=charts_builder.order_sort)
    # The invalid key goes first.
    assert 'order' not in res[0]
    # The remaining will be offset since the first one has no key.
    for i in range(0, 10):
        if 'order' in res[i]:
            assert res[i]['order'] == i - 1


def test_app_redirects(ctx, client):
    app, test = client
    res = test.get('/charts')
    assert REDIRECT_MSG in str(res.data)


def test_routes(ctx, client):
    assert url_for('jsondash.dashboard') == '/charts/'
    assert url_for('jsondash.view', c_id='foo') == '/charts/foo'
    assert url_for('jsondash.update', c_id='foo') == '/charts/foo/update'
    assert url_for('jsondash.clone', c_id='foo') == '/charts/foo/clone'
    assert url_for('jsondash.delete', c_id='foo') == '/charts/foo/delete'
    assert url_for('jsondash.create') == '/charts/create'


def test_get_dashboard_contains_all_chart_types_list(monkeypatch, ctx, client):
    app, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    res = test.get(url_for('jsondash.dashboard'))
    for family, config in settings.CHARTS_CONFIG.items():
        for chart in config['charts']:
            _, label = chart
            assert label in str(res.data)


def test_get_dashboard_contains_no_chart_msg(monkeypatch, ctx, client):
    app, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    res = str(test.get(url_for('jsondash.dashboard')).data)
    assert 'No dashboards exist. Create one below to get started.' in res


def test_create_dashboards_check_index_count(monkeypatch, ctx, client):
    app, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    for i in range(10):
        data = dict(name=i, modules=[])
        res = test.post(url_for('jsondash.create'), data=data)
    res = test.get(url_for('jsondash.dashboard'))
    assert len(read()) == 10
    heading = pq(res.data).find('h1.lead').text()
    assert 'Showing 10 dashboards with 0 charts' in heading


def test_get_view_valid_id_invalid_config(monkeypatch, ctx, client):
    app, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    view = dict(modules=[dict(foo='bar')])
    readfunc = read(override=dict(view))
    monkeypatch.setattr(charts_builder.adapter, 'read', readfunc)
    with pytest.raises(ValueError):
        res = test.get(url_for('jsondash.view', c_id='123'))
        assert 'Invalid config!' in str(res.data)


def test_get_view_valid_id_invalid_modules(monkeypatch, ctx, client):
    app, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    view = dict(id='123')
    readfunc = read(override=dict(view))
    monkeypatch.setattr(charts_builder.adapter, 'read', readfunc)
    res = test.get(
        url_for('jsondash.view', c_id='123'),
        follow_redirects=True)
    assert 'Invalid configuration - missing modules.' in str(res.data)


def test_get_view_valid_id_ensure__id_popped(monkeypatch, ctx, client):
    app, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    view = get_json_config('inputs.json')
    view = dict(view)
    view.update(_id='foo')
    readfunc = read(override=view)
    monkeypatch.setattr(charts_builder.adapter, 'read', readfunc)
    res = test.get(url_for('jsondash.view', c_id=view['id']))
    dom = pq(res.data)
    assert len(dom.find('.item')) == len(view['modules'])


def test_view_valid_dashboard_count_and_inputs(monkeypatch, ctx, client):
    app, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    view = get_json_config('inputs.json')
    readfunc = read(override=dict(view))
    monkeypatch.setattr(charts_builder.adapter, 'read', readfunc)
    res = test.get(url_for('jsondash.view', c_id=view['id']))
    dom = pq(res.data)
    assert len(dom.find('.item')) == len(view['modules'])
    assert len(dom.find('.charts-input-icon')) == 1


def test_view_valid_dashboard_inputs_form(monkeypatch, ctx, client):
    app, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    view = get_json_config('inputs.json')
    readfunc = read(override=dict(view))
    monkeypatch.setattr(charts_builder.adapter, 'read', readfunc)
    res = test.get(url_for('jsondash.view', c_id=view['id']))
    dom = pq(res.data)
    charts_with_inputs = [m for m in view['modules'] if 'inputs' in m]
    num_config_inputs = len(charts_with_inputs[0]['inputs']['options'])
    assert num_config_inputs == 5  # Sanity check
    assert len(charts_with_inputs) == 1
    assert len(dom.find('.chart-inputs')) == 1
    assert dom.find('.chart-inputs').hasClass('collapse')
    # There are 7 input fields generated for this particular json file.
    assert len(dom.find('.chart-inputs form input')) == 7


def test_view_valid_dashboard_inputs_form_counts(monkeypatch, ctx, client):
    app, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    view = get_json_config('inputs.json')
    readfunc = read(override=dict(view))
    monkeypatch.setattr(charts_builder.adapter, 'read', readfunc)
    res = test.get(url_for('jsondash.view', c_id=view['id']))
    dom = pq(res.data)
    charts_with_inputs = [m for m in view['modules'] if 'inputs' in m]
    input_options = charts_with_inputs[0]['inputs']['options']
    radio_opts = [o for o in input_options if o['type'] == 'radio'][0]
    radio_opts = radio_opts['options']
    assert len(dom.find('.chart-inputs form .input-radio')) == len(radio_opts)
    select = [o for o in input_options if o['type'] == 'select']
    assert len(dom.find('.chart-inputs form select')) == len(select)
    options = select[0]['options']
    assert len(dom.find('.chart-inputs form select option')) == len(options)
    numbers = [inp for inp in input_options if inp['type'] == 'number']
    assert len(dom.find('.chart-inputs [type="number"]')) == len(numbers)
    text = [inp for inp in input_options if inp['type'] == 'text']
    assert len(dom.find('.chart-inputs [type="text"]')) == len(text)
    checkbox = [inp for inp in input_options if inp['type'] == 'checkbox']
    assert len(dom.find('.chart-inputs [type="checkbox"]')) == len(checkbox)


def test_get_view_valid_modules_valid_dash_title(monkeypatch, ctx, client):
    app, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    view = get_json_config('inputs.json')
    readfunc = read(override=dict(view))
    monkeypatch.setattr(charts_builder.adapter, 'read', readfunc)
    res = test.get(url_for('jsondash.view', c_id=view['id']))
    dom = pq(res.data)
    assert dom.find('.dashboard-title').text() == view['name']


@pytest.mark.invalid_id_redirect
def test_get_view_invalid_id_redirect(monkeypatch, ctx, client):
    app, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    res = test.get(url_for('jsondash.view', c_id='123'))
    assert REDIRECT_MSG in str(res.data)


def test_create_valid(monkeypatch, ctx, client):
    app, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    res = test.post(
        url_for('jsondash.create'),
        data=dict(name='mydash-valid'),
        follow_redirects=True)
    dom = pq(res.data)
    flash_msg = 'Created new dashboard "mydash-valid"'
    assert dom.find('.alert-info').text() == flash_msg


@pytest.mark.invalid_id_redirect
def test_clone_invalid_id_redirect(monkeypatch, ctx, client):
    app, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    res = test.post(url_for('jsondash.clone', c_id='123'))
    assert REDIRECT_MSG in str(res.data)


def test_clone_valid(monkeypatch, ctx, client):
    app, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    assert len(read()) == 0
    res = test.post(url_for('jsondash.create'),
                    data=dict(name='mydash', modules=[]),
                    follow_redirects=True)
    dom = pq(res.data)
    new_id = read()[0]['id']
    assert read()[0]['name'] == 'mydash'
    flash_msg = 'Created new dashboard "mydash"'
    assert dom.find('.alert-info').text() == flash_msg
    assert len(read()) == 1
    assert read()[0]['name'] == 'mydash'
    res = test.post(
        url_for('jsondash.clone', c_id=new_id),
        follow_redirects=True)
    dom = pq(res.data)
    flash_msg = 'Created new dashboard clone "Clone of mydash"'
    assert flash_msg in dom.find('.alert').text()
    assert len(read()) == 2


@pytest.mark.invalid_id_redirect
def test_delete_invalid_id_redirect(monkeypatch, ctx, client):
    app, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    res = test.post(
        url_for('jsondash.delete', c_id='123'))
    assert REDIRECT_MSG in str(res.data)


def test_delete_valid(monkeypatch, ctx, client):
    app, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    view = dict(name='mydash', modules=[])
    readfunc = read(override=dict(view))
    monkeypatch.setattr(charts_builder.adapter, 'read', readfunc)
    assert not read()
    # Create first one.
    res = test.post(url_for('jsondash.create'),
                    data=view,
                    follow_redirects=True)
    assert len(read()) == 1
    view_id = read()[0]['id']
    dom = pq(res.data)
    flash_msg = 'Created new dashboard "mydash"'
    assert dom.find('.alert-info').text() == flash_msg
    assert len(read()) == 1
    res = test.post(url_for('jsondash.delete', c_id=view_id),
                    follow_redirects=True)
    dom = pq(res.data)
    flash_msg = 'Deleted dashboard "{}"'.format(view_id)
    assert dom.find('.alert-info').text() == flash_msg
    assert len(read()) == 0


@pytest.mark.invalid_id_redirect
def test_update_invalid_id_redirect(monkeypatch, ctx, client):
    app, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    res = test.post(url_for('jsondash.update', c_id='123'))
    assert REDIRECT_MSG in str(res.data)


def test_update_invalid_config(monkeypatch, ctx, client):
    app, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    view = get_json_config('inputs.json')
    readfunc = read(override=dict(view))
    monkeypatch.setattr(charts_builder.adapter, 'read', readfunc)
    res = test.post(
        url_for('jsondash.update', c_id=view['id']),
        data={'edit-raw': 'on'},
        follow_redirects=True)
    dom = pq(res.data)
    assert dom.find('.alert-danger').text() == 'Error: Invalid JSON config.'


def test_update_valid(monkeypatch, ctx, client):
    app, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    assert not read()
    res = test.post(
        url_for('jsondash.create'),
        data=dict(name='newname', modules=[]),
        follow_redirects=True)
    assert len(read()) == 1
    view_id = read()[0]['id']
    res = test.post(
        url_for('jsondash.update', c_id=view_id),
        data=dict(name='newname'),
        follow_redirects=True)
    dom = pq(res.data)
    flash_msg = 'Updated view "{}"'.format(view_id)
    assert dom.find('.alert-info').text() == flash_msg
    assert len(read()) == 1
