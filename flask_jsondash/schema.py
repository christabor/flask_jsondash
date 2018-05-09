# -*- coding: utf-8 -*-

"""
flask_jsondash.schema
~~~~~~~~~~~~~~~~~~~~~

The core schema definition and validation rules.

:copyright: (c) 2016 by Chris Tabor.
:license: MIT, see LICENSE for more details.
"""

import json

import cerberus

from flask_jsondash.settings import CHARTS_CONFIG


class InvalidSchemaError(ValueError):
    """Wrapper exception for specific raising scenarios."""


def get_chart_types():
    """Get all available chart 'type' names from core config.

    Returns:
        types (list): A list of all possible chart types, under all families.
    """
    types = []
    charts = [chart['charts'] for chart in CHARTS_CONFIG.values()]
    for group in charts:
        for chart in group:
            types.append(chart[0])
    return types


CHART_INPUT_SCHEMA = {
    'btn_classes': {
        'type': 'list',
        'schema': {
            'type': 'string',
        },
    },
    'submit_text': {
        'type': 'string',
    },
    'options': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'options': {
                    'type': 'list',
                    'schema': {
                        # E.g. [10, 'Select 10'],
                        'type': 'list',
                        'minlength': 2,
                        'maxlength': 2,
                    },
                },
                'type': {
                    'type': 'string',
                    'allowed': [
                        'number', 'select', 'radio',
                        'checkbox', 'text',
                        'password',
                        # HTML5
                        'color',
                        'date',
                        'datetime-local',
                        'month',
                        'week',
                        'time',
                        'email',
                        'number',
                        'range',
                        'search',
                        'tel',
                        'url',
                    ],
                    'default': 'text',
                },
                'name': {
                    'type': 'string',
                    'required': True,
                },
                'default': {
                    'anyof': [
                        {'type': 'string'},
                        {'type': 'number'},
                        {'type': 'boolean'},
                    ],
                    'nullable': True,
                },
                'validator_regex': {
                    'nullable': True,
                    'type': 'string',
                },
                'placeholder': {
                    'nullable': True,
                    'anyof': [
                        {'type': 'string'},
                        {'type': 'number'},
                    ]
                },
                'label': {
                    'type': 'string',
                },
                'input_classes': {
                    'type': 'list',
                    'schema': {
                        'type': 'string',
                    },
                },
            },
        },
    },
}
CHART_SCHEMA = {
    'type': 'dict',
    'schema': {
        'name': {
            'type': 'string',
            'required': True,
        },
        'guid': {
            'type': 'string',
            'required': True,
            # 5-"section" regex
            # this might not be necessary but it's
            # useful to enforce a truly globally unique id,
            # especially for usage with the js API.
            'regex': (
                '[a-zA-Z0-9]+-[a-zA-Z0-9]+-'
                '[a-zA-Z0-9]+-[a-zA-Z0-9]+-[a-zA-Z0-9]+'
            ),
        },
        'order': {
            'type': 'number',
            'nullable': True,
            'default': 0,
        },
        'row': {
            'type': 'number',
            'nullable': True,
            'default': 0,
        },
        'refresh': {
            'type': 'boolean',
            'nullable': True,
        },
        'refreshInterval': {
            'type': 'number',
            'nullable': True,
        },
        'height': {
            'type': 'number',
            'required': True,
        },
        'width': {
            'anyof': [
                {'type': 'string'},
                {'type': 'number'},
            ],
            # TODO: check this works
            # This regex allows the overloading
            # of this property to allow for
            # grid widths (e.g. "col-8") vs number widths.
            'regex': '(col-[0-9]+)|([0-9]+)',
            'required': True,
        },
        'dataSource': {
            'type': 'string',
            'required': True,
        },
        'family': {
            'type': 'string',
            'required': True,
            'allowed': list(CHARTS_CONFIG.keys()),
        },
        'key': {
            'type': 'string',
            'required': False,
        },
        'type': {
            'type': 'string',
            'required': True,
            'allowed': get_chart_types(),
        },
        'inputs': {
            'type': 'dict',
            'schema': CHART_INPUT_SCHEMA
        },
    },
}
DASHBOARD_SCHEMA = {
    'name': {
        'type': 'string',
        'required': True,
    },
    'id': {
        'type': 'string',
        'required': True,
        'regex': (
            '[a-zA-Z0-9]+-[a-zA-Z0-9]+-'
            '[a-zA-Z0-9]+-[a-zA-Z0-9]+-[a-zA-Z0-9]+'
        ),
    },
    'date': {
        'type': 'string',
        'required': True,
    },
    'layout': {
        'type': 'string',
        'required': True,
        'allowed': ['freeform', 'grid'],
    },
    'category': {
        'type': 'string',
        'required': False,
    },
    'modules': {
        'type': 'list',
        'schema': CHART_SCHEMA,
        'required': True,
    },
}


def validate(conf):
    """Validate a json conf."""
    v = cerberus.Validator(DASHBOARD_SCHEMA, allow_unknown=True)
    valid = v.validate(conf)
    if not valid:
        return v.errors


def is_consecutive_rows(lst):
    """Check if a list of integers is consecutive.

    Args:
        lst (list): The list of integers.

    Returns:
        True/False: If the list contains consecutive integers.

    Originally taken from and modified:
        http://stackoverflow.com/
            questions/40091617/test-for-consecutive-numbers-in-list
    """
    assert 0 not in lst, '0th index is invalid!'
    lst = list(set(lst))
    if not lst:
        return True
    setl = set(lst)
    return len(lst) == len(setl) and setl == set(range(min(lst), max(lst) + 1))


def validate_raw_json_grid(conf):
    """Grid mode specific validations.

    Args:
        conf (dict): The dashboard configuration.

    Raises:
        InvalidSchemaError: If there are any issues with the schema

    Returns:
        None: If no errors were found.
    """
    layout = conf.get('layout', 'freeform')
    fixed_only_required = ['row']
    rows = []
    modules = conf.get('modules', [])
    valid_cols = ['col-{}'.format(i) for i in range(1, 13)]
    if not modules:
        return
    for module in modules:
        try:
            rows.append(int(module.get('row')))
        except TypeError:
            raise InvalidSchemaError(
                'Invalid row value for module "{}"'.format(module.get('name')))
    if not is_consecutive_rows(rows):
        raise InvalidSchemaError(
            'Row order is not consecutive: "{}"!'.format(sorted(rows)))
    for module in modules:
        width = module.get('width')
        if width not in valid_cols:
            raise InvalidSchemaError(
                'Invalid width for grid format: "{}"'.format(width))
        for field in fixed_only_required:
            if field not in module and layout == 'grid':
                ident = module.get('name', module)
                raise InvalidSchemaError(
                    'Invalid JSON. "{}" must be '
                    'included in "{}" for '
                    'fixed grid layouts'.format(field, ident))


def validate_raw_json(jsonstr, **overrides):
    """Validate the raw json for a config.

    Args:
        jsonstr (str): The raw json configuration
        **overrides: Any key/value pairs to override in the config.
            Used only for setting default values that the user should
            never enter but are required to validate the schema.

    Raises:
        InvalidSchemaError: If there are any issues with the schema

    Returns:
        data (dict): The parsed configuration data
    """
    data = json.loads(jsonstr)
    data.update(**overrides)
    layout = data.get('layout', 'freeform')

    if layout == 'grid':
        validate_raw_json_grid(data)
    else:
        for module in data.get('modules', []):
            width = module.get('width')
            try:
                int(width)
            except (TypeError, ValueError):
                raise InvalidSchemaError(
                    'Invalid value for width in `freeform` layout.')
            if module.get('row') is not None:
                raise InvalidSchemaError(
                    'Cannot mix `row` with `freeform` layout.')
    results = validate(data)
    if results is not None:
        raise InvalidSchemaError(results)
    return data
