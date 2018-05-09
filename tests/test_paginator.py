from flask import url_for

from pyquery import PyQuery as pq

from flask_jsondash import charts_builder, utils

from conftest import (
    auth_valid,
    read,
)


def make_count(num=1000):
    def count(*args, **kwargs):
        return num
    return count


def make_setting(num=30):
    def setting(*args, **kwargs):
        return num
    return setting


def check_values(paginator, limit, perpage, currpage, skip, numpages, count):
    assert isinstance(paginator, utils.Paginator)
    assert paginator.limit == limit
    assert paginator.per_page == perpage
    assert paginator.curr_page == currpage
    assert paginator.skip == skip
    assert paginator.num_pages == list(numpages)
    assert paginator.count == count


def test_paginator_default_usage(monkeypatch, client):
    app, test = client
    monkeypatch.setattr(utils, 'setting', make_setting(30))
    monkeypatch.setattr(utils.adapter, 'count', make_count(1000))
    paginator = utils.paginator(page=0)
    check_values(paginator, 30, 30, 0, 0, range(1, 35), 1000)


def test_paginator_norecords(monkeypatch, client):
    app, test = client
    monkeypatch.setattr(utils, 'setting', make_setting(30))
    monkeypatch.setattr(utils.adapter, 'count', make_count(0))
    paginator = utils.paginator(page=0)
    check_values(paginator, 30, 30, 0, 0, [], 0)


def test_paginator_default_fallback_data_lt_2(monkeypatch, client):
    app, test = client
    monkeypatch.setattr(utils, 'setting', make_setting(0))
    monkeypatch.setattr(utils.adapter, 'count', make_count(0))
    paginator = utils.paginator(page=None, per_page=1, count=None)
    check_values(paginator, 2, 2, 0, 0, [], 0)


def test_paginator_bad_kwargs_fallback_data(monkeypatch, client):
    app, test = client
    monkeypatch.setattr(utils, 'setting', make_setting(0))
    monkeypatch.setattr(utils.adapter, 'count', make_count(0))
    # Ensure the paginator uses a minimum of 2 per page to prevent
    # division errors, even when there are no good values sent,
    # AND the app default setting is forcibly invalid (set to 0)
    paginator = utils.paginator(
        page=None, per_page=None, count=None)
    check_values(paginator, 2, 2, 0, 0, [], 0)


def test_create_dashboards_check_paginator_html(monkeypatch, ctx, client):
    app, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    for i in range(100):
        data = dict(name=i, modules=[])
        res = test.post(url_for('jsondash.create'), data=data)
    res = test.get(url_for('jsondash.dashboard'))
    dom = pq(res.data)
    assert len(read()) == 100
    assert dom.find('.paginator-status').text() == 'Showing 0-25 of 100 results'
    res = test.get(url_for('jsondash.dashboard') + '?page=2')
    dom = pq(res.data)
    assert dom.find(
        '.paginator-status').text() == 'Showing 25-50 of 100 results'
    res = test.get(url_for('jsondash.dashboard') + '?page=3')
    dom = pq(res.data)
    assert dom.find(
        '.paginator-status').text() == 'Showing 50-75 of 100 results'
    res = test.get(url_for('jsondash.dashboard') + '?page=4')
    dom = pq(res.data)
    assert dom.find(
        '.paginator-status').text() == 'Showing 75-100 of 100 results'
