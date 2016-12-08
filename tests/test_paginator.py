from flask import (
    Flask,
    current_app,
    url_for,
)

from pyquery import PyQuery as pq

from flask_jsondash import charts_builder

from conftest import (
    URL_BASE,
    auth_ok,
    read,
    update,
)


def make_count(num=1000):
    def count(*args, **kwargs):
        return num
    return count


def make_setting(num=30):
    def setting(*args, **kwargs):
        return 30
    return setting


def check_values(paginator, limit, perpage, currpage, skip, numpages, count):
    assert isinstance(paginator, charts_builder.Paginator)
    assert paginator.limit == limit
    assert paginator.per_page == perpage
    assert paginator.curr_page == currpage
    assert paginator.skip == skip
    assert paginator.num_pages == list(numpages)
    assert paginator.count == count


def test_paginator_default_usage(monkeypatch, client):
    app, test = client
    monkeypatch.setattr(charts_builder, 'setting', make_setting(30))
    monkeypatch.setattr(charts_builder.adapter, 'count', make_count(1000))
    paginator = charts_builder.paginator(page=0)
    check_values(paginator, 30, 30, 0, 0, range(1, 35), 1000)


def test_paginator_norecords(monkeypatch, client):
    app, test = client
    monkeypatch.setattr(charts_builder, 'setting', make_setting(30))
    monkeypatch.setattr(charts_builder.adapter, 'count', make_count(0))
    paginator = charts_builder.paginator(page=0)
    check_values(paginator, 30, 30, 0, 0, [], 0)


def test_paginator_default_fallback_data(monkeypatch, client):
    app, test = client
    monkeypatch.setattr(charts_builder, 'setting', make_setting(0))
    monkeypatch.setattr(charts_builder.adapter, 'count', make_count(0))
    paginator = charts_builder.paginator(page=None, per_page=1, count=None)
    check_values(paginator, 2, 2, 0, 0, [], 0)


def test_paginator_bad_kwargs(monkeypatch, client):
    app, test = client
    monkeypatch.setattr(charts_builder, 'setting', make_setting(0))
    monkeypatch.setattr(charts_builder.adapter, 'count', make_count(0))
    paginator = charts_builder.paginator(
        page=None, per_page=None, count=None)
    check_values(paginator, 30, 30, 0, 0, [], 0)


def test_create_dashboards_check_paginator_html(monkeypatch, ctx, client):
    app, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_ok)
    for i in range(100):
        data = dict(name=i, modules=[])
        res = test.post(url_for('jsondash.create'), data=data)
    res = test.get(url_for('jsondash.dashboard'))
    dom = pq(res.data)
    assert len(read()) == 100
    assert dom.find('.paginator-status').text() == 'Showing 0-25 of 100 results'
    res = test.get(url_for('jsondash.dashboard') + '?page=2')
    dom = pq(res.data)
    assert dom.find('.paginator-status').text() == 'Showing 25-50 of 100 results'
    res = test.get(url_for('jsondash.dashboard') + '?page=3')
    dom = pq(res.data)
    assert dom.find('.paginator-status').text() == 'Showing 50-75 of 100 results'
    res = test.get(url_for('jsondash.dashboard') + '?page=4')
    dom = pq(res.data)
    assert dom.find('.paginator-status').text() == 'Showing 75-100 of 100 results'
