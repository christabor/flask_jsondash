from random import shuffle

import pytest

from flask_jsondash import schema, charts_builder, utils


@pytest.mark.schema
@pytest.mark.parametrize('lst', [
    [1, 2, 3],
    [1, 1, 2, 2, 3],
    [],  # Handles empty case as true
])
def test_is_consecutive_rows_normal(lst):
    assert schema.is_consecutive_rows(lst)


@pytest.mark.schema
@pytest.mark.parametrize('lst', [
    [1, 2, 3, 10],
    [1, 1, 2, 4],
    range(1, 100, 2),
])
def test_is_consecutive_rows_invalid(lst):
    assert not schema.is_consecutive_rows(lst)


@pytest.mark.schema
@pytest.mark.parametrize('lst', [
    [1, 0, 2],
    [0, 1],
    [1, 0],
])
def test_is_consecutive_rows_invalid_no_row_zero_allowed(lst):
    with pytest.raises(AssertionError):
        schema.is_consecutive_rows(lst)


@pytest.mark.utils
def test_get_num_rows_none():
    assert utils.get_num_rows(None) is None


@pytest.mark.utils
def test_get_num_rows_freeform():
    assert utils.get_num_rows(dict(layout='freeform')) is None


@pytest.mark.utils
def test_get_num_rows_fixed():
    conf = dict(
        layout='grid',
        modules=[dict(row=1), dict(row=2)],
    )
    assert utils.get_num_rows(conf) == 2


@pytest.mark.utils
def test_order_sort_none():
    assert utils.order_sort(None) == -1


@pytest.mark.utils
def test_order_sort_force_valueerror():
    item = dict(order='NaN')
    assert utils.order_sort(item) == -1


@pytest.mark.utils
def test_order_sort_force_valueerror_func():
    item = dict(order=lambda x: x)
    assert utils.order_sort(item) == -1


@pytest.mark.utils
def test_order_sort_force_valueerror_none():
    item = dict(order=None)
    assert utils.order_sort(item) == -1


@pytest.mark.utils
def test_order_sort_invalid_key():
    item = dict()
    assert utils.order_sort(item) == -1


@pytest.mark.utils
def test_order_sort_valid_key():
    item = dict(order=1)
    assert utils.order_sort(item) == 1


@pytest.mark.utils
def test_order_shuffled_sort_multiple_valid_key():
    orders = list(range(0, 10))
    shuffle(orders)
    modules = [dict(order=i, foo='bar') for i in orders]
    res = sorted(modules, key=utils.order_sort)
    for i in range(0, 10):
        assert res[i]['order'] == i


@pytest.mark.utils
def test_order_shuffled_sort_multiple_valid_key_one_invalid_key():
    orders = list(range(0, 10))
    shuffle(orders)
    modules = [dict(order=i, foo='bar') for i in orders]
    # Add one w/o order key.
    modules.append(dict(foo='bar'))
    res = sorted(modules, key=utils.order_sort)
    # The invalid key goes first.
    assert 'order' not in res[0]
    # The remaining will be offset since the first one has no key.
    for i in range(0, 10):
        if 'order' in res[i]:
            assert res[i]['order'] == i - 1


def test_get_all_assets():
    # Test that all assets are simply the right filetype and that they exist.
    res = charts_builder.get_all_assets()
    assert isinstance(res['css'], list)
    assert isinstance(res['js'], list)
    for url in res['js']:
        assert isinstance(url, str)
        assert url.endswith('.js')
    for url in res['css']:
        assert isinstance(url, str)
        assert url.endswith('.css')


def test_get_active_assets():
    all_res = charts_builder.get_all_assets()
    families = ['D3']
    active_res = charts_builder.get_active_assets(families)
    assert all_res != active_res


def test_get_active_assets_ensure_no_duplicates():
    all_res = charts_builder.get_all_assets()
    families = ['D3', 'D3', 'C3', 'C3']
    active_res = charts_builder.get_active_assets(families)
    assert all_res != active_res


def test_get_active_assets_ensure_deps_loaded_first():
    # Ensure that assets that require dependencies have the deps
    # loaded FIRST.
    active_res = charts_builder.get_active_assets(['D3', 'C3'])
    assert active_res['css'][0].endswith('c3.min.css')
    assert active_res['js'][0].endswith('d3.min.js')
    # c3 depends on d3.
    assert active_res['js'][1].endswith('c3.min.js')
