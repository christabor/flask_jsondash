from uuid import uuid1
import json

import pytest

from flask_jsondash.data_utils import filetree


def test_path_hierarchy(tmpdir):
    uid = uuid1()
    tmpfile = tmpdir.mkdir('{}'.format(uid))
    data = filetree.path_hierarchy(tmpfile.strpath)
    assert json.dumps(data)
    for key in ['type', 'name', 'path']:
        assert key in data


def test_path_hierarchy_invalid_path(tmpdir):
    with pytest.raises(OSError):
        filetree.path_hierarchy('invalid-path')
