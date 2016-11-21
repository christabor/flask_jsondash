from flask import (
    Flask,
    current_app,
    url_for,
)

from flask_jsondash import charts_builder


def make_count(num=1000):
    def count(*args, **kwargs):
        return num
    return count


def make_setting(num=30):
    def setting(*args, **kwargs):
        return 30
    return setting


def test_paginator_default(monkeypatch, client):
    app, test = client
    with app.app_context():
        monkeypatch.setattr(charts_builder, 'setting', make_setting(30))
        monkeypatch.setattr(charts_builder.adapter, 'count', make_count(1000))
        paginator = charts_builder.paginator(0)
        assert isinstance(paginator, charts_builder.Paginator)
        assert paginator.limit == 30
        assert paginator.per_page == 30
        assert paginator.curr_page == 0
        assert paginator.skip == 0
        assert paginator.num_pages == range(1, 35)
        assert paginator.count == 1000


def test_paginator_norecords(monkeypatch, client):
    app, test = client
    with app.app_context():
        monkeypatch.setattr(charts_builder, 'setting', make_setting(30))
        monkeypatch.setattr(charts_builder.adapter, 'count', make_count(0))
        paginator = charts_builder.paginator(0)
        assert isinstance(paginator, charts_builder.Paginator)
        assert paginator.limit == 30
        assert paginator.per_page == 30
        assert paginator.curr_page == 0
        assert paginator.skip == 0
        assert paginator.num_pages == []
        assert paginator.count == 0
