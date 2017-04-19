import json

from datetime import datetime as dt

import pytest

from flask_jsondash import charts_builder

# Py2/3 compat.
try:
    _unicode = unicode
except NameError:
    _unicode = str


@pytest.mark.filters
def test_getdims_normal(ctx, client):
    app, test = client
    data = dict(width=100, height=100, dataSource='...', type='sometype')
    expected = dict(width=100, height=100)
    assert charts_builder.get_dims(object, data) == expected


@pytest.mark.parametrize('field', [
    'width',
    'height',
    'dataSource',
])
@pytest.mark.filters
def test_getdims_missing_all_expected(ctx, client, field):
    app, test = client
    data = dict(width=100, height=100, dataSource='...', type='sometype')
    del data[field]
    with pytest.raises(ValueError):
        charts_builder.get_dims(object, data)


@pytest.mark.filters
def test_getdims_youtube_invalid_url(ctx, client):
    app, test = client
    data = dict(type='youtube', dataSource=None, width=100, height=100)
    with pytest.raises(ValueError):
        charts_builder.get_dims(object, data)


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
def test_getdims_youtube_fixedgrid_width_adjusted_height_same(ctx, client):
    app, test = client
    yt = ('<iframe width="650" height="366" '
          'src="https://www.youtube.com/embed/'
          '_hI0qMtdfng?list=RD_hI0qMtdfng&amp;'
          'controls=0&amp;showinfo=0" frameborder="0"'
          ' allowfullscreen></iframe>')
    data = dict(type='youtube', dataSource=yt, width='col-6', height=100)
    expected = dict(width='6', height=100)
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
