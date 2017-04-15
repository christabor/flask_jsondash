import json
import pytest

from flask_jsondash import charts_builder as app


def _schema(**vals):
    """Default schema."""
    data = dict(
        date="2016-08-23 15:03:49.178000",
        layout="grid",
        name="testlayout",
        modules=[],
    )
    data.update(**vals)
    return json.dumps(data)


@pytest.mark.schema
def test_validate_raw_json_valid_empty_modules():
    assert app.validate_raw_json(_schema())


@pytest.mark.schema
def test_validate_raw_json_valid_freeform():
    d = _schema(
        layout='freeform',
        modules=[
            dict(name='foo', dataSource='foo',
                 width=1, height=1, type='line',
                 family='C3')]
    )
    assert app.validate_raw_json(d)


@pytest.mark.schema
def test_validate_raw_json_valid_fixed():
    d = _schema(
        layout='freeform',
        modules=[
            dict(name='foo', dataSource='foo',
                 width=1, height=1, type='line',
                 family='C3')]
    )
    assert app.validate_raw_json(d)


@pytest.mark.schema
@pytest.mark.parametrize('field', [
    'type',
    'family',
    'width',
    'height',
    'dataSource',
])
def test_validate_raw_json_missing_required_module_keys(field):
    module = dict(
        name='foo', dataSource='foo',
        width=1, height=1, type='line',
        family='C3')
    del module[field]
    d = _schema(
        layout='grid',
        modules=[module]
    )
    with pytest.raises(app.InvalidSchemaError):
        app.validate_raw_json(d)


@pytest.mark.schema
@pytest.mark.parametrize('field', [
    'row',
])
def test_validate_raw_json_missing_required_fixedgrid_module_keys(field):
    module = dict(
        name='foo', dataSource='foo',
        width=1, height=1, type='line',
        row=1, family='C3')
    del module[field]
    d = _schema(
        layout='grid',
        modules=[module]
    )
    with pytest.raises(app.InvalidSchemaError):
        app.validate_raw_json(d)


@pytest.mark.schema
@pytest.mark.parametrize('field', [
    'row',
])
def test_validate_raw_json_missing_optional_freeform_module_keys(field):
    # Ensure that required fields for fixed grid
    # are not required for freeform layouts.
    module = dict(
        name='foo', dataSource='foo',
        width=1, height=1, type='line',
        row=1, family='C3')
    del module[field]
    d = _schema(
        layout='freeform',
        modules=[module]
    )
    assert app.validate_raw_json(d)
