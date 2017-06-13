# -*- coding: utf-8 -*-

"""
flask_jsondash.schema
~~~~~~~~~~~~~~~~~~~~~

The core schema definition and validation rules.

:copyright: (c) 2016 by Chris Tabor.
:license: MIT, see LICENSE for more details.
"""

import cerberus

from .settings import CHARTS_CONFIG


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
