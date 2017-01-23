import json

from uuid import uuid1

import pytest

from click.testing import CliRunner

from flask_jsondash.data_utils import filetree


def test_path_hierarchy(tmpdir):
    uid = uuid1()
    tmp = tmpdir.mkdir('{}'.format(uid))
    data = filetree.path_hierarchy(tmp.strpath)
    assert json.dumps(data)
    for key in ['type', 'name', 'path']:
        assert key in data


def test_path_hierarchy_invalid_path(tmpdir):
    with pytest.raises(OSError):
        filetree.path_hierarchy('invalid-path')


def test_path_hierarchy_invalid_path_none(tmpdir):
    with pytest.raises(AssertionError):
        filetree.path_hierarchy(None)


def test_path_hierarchy_invalid_path_empty_path(tmpdir):
    with pytest.raises(OSError):
        filetree.path_hierarchy('')


def test_get_tree_invalid_path(tmpdir):
    runner = CliRunner()
    result = runner.invoke(filetree.get_tree, ['-p', '/{}'.format(uuid1())])
    assert result.exit_code == -1
    assert isinstance(result.exception, OSError)
    assert 'No such file or directory' in str(result.exception)


def test_get_tree_valid_path(tmpdir):
    uid = str(uuid1())
    tmp = tmpdir.mkdir(uid)
    runner = CliRunner()
    result = runner.invoke(filetree.get_tree, ['-p', tmp.strpath])
    assert result.exit_code == 0
    assert 'path' in result.output
    assert 'name' in result.output
    assert 'type' in result.output
    assert 'children' in result.output


def test_get_tree_valid_path_jsonfile(tmpdir):
    uid = str(uuid1())
    tmp = tmpdir.mkdir(uid)
    jsonfile = tmp.join('foo.json')
    jsonpath = str(jsonfile.realpath()).encode('utf-8')
    jsonfile.write('')
    assert str(jsonfile.read()) == ''
    runner = CliRunner()
    result = runner.invoke(
        filetree.get_tree, ['-p', tmp.strpath, '-j', jsonpath])
    assert result.exit_code == 0
    data = str(jsonfile.read())
    assert 'path' in data
    assert 'name' in data
    assert 'type' in data
    assert 'children' in data


def test_get_tree_valid_path_prettyprint(tmpdir):
    uid = str(uuid1())
    tmp = tmpdir.mkdir(uid)
    runner = CliRunner()
    result = runner.invoke(
        filetree.get_tree, ['-p', tmp.strpath, '--ppr'])
    assert result.exit_code == 0
    assert 'path' in result.output
    assert 'name' in result.output
    assert 'type' in result.output
    assert 'children' in result.output
