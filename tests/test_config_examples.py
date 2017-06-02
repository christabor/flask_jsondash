"""
Test the validation for the core configuration schema.

Also test any example config files.
"""

import os
import json
import pytest

from flask_jsondash import schema


ROOT_DIR = 'example_app/examples/config'


def get_example_configs():
    return [
        f for f in os.listdir(ROOT_DIR)
        if f.endswith('.json')
    ]


@pytest.mark.schema
@pytest.mark.examples
@pytest.mark.parametrize('conf', get_example_configs())
def test_example_configs_from_example_folder_load_as_valid_json(conf):
    data = open('{}/{}'.format(ROOT_DIR, conf)).read()
    assert json.loads(data)


@pytest.mark.schema
@pytest.mark.validation
@pytest.mark.examples
@pytest.mark.parametrize('conf', get_example_configs())
def test_example_configs_from_example_folder_load_as_valid_schema(conf):
    data = open('{}/{}'.format(ROOT_DIR, conf)).read()
    data = json.loads(data)
    res = schema.validate(data)
    assert res is None
