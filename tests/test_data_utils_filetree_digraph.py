from uuid import uuid1

import pytest

from click.testing import CliRunner

from flask_jsondash.data_utils import filetree_digraph


# def test_make_dotfile(tmpdir):
#     uid = str(uuid1())
#     tmp = tmpdir.mkdir(uid)
#     for i in range(4):
#         tmp.join('{}.txt'.format(i)).write('{}'.format(i))
#     data = filetree_digraph.make_dotfile(tmp.strpath)
#     # Ensure wrapping lines are proper digraph format.
#     assert data.startswith('digraph {\n')
#     assert data.endswith('\n}\n')
#     lines = data.split('\n')
#     # Ensure each line has the right dotfile format.
#     for i, line in enumerate(lines[1:len(lines) - 2]):
#         assert line == '\t"{0}" -> "{1}.txt";'.format(uid, i)


def test_make_dotfile_skip_empty(monkeypatch, tmpdir):
    uid = str(uuid1())
    tmp = tmpdir.mkdir(uid)
    # Add a bunch of empty pointers
    results = [' ->' for _ in range(10)] + ['foo -> bar']
    monkeypatch.setattr(
        filetree_digraph, 'path_hierarchy', lambda *a, **k: results)
    data = filetree_digraph.make_dotfile(tmp.strpath)
    assert data == 'digraph {\n\tfoo -> bar;\n}\n'


def test_make_dotfile_invalid_path():
    with pytest.raises(OSError):
        filetree_digraph.make_dotfile('invalid-path')


def test_make_dotfile_invalid_path_none():
    with pytest.raises(AssertionError):
        filetree_digraph.make_dotfile(None)


def test_get_dotfile_tree_invalid_path(tmpdir):
    runner = CliRunner()
    result = runner.invoke(filetree_digraph.get_dotfile_tree, ['-p', '.'])
    assert result.exit_code == -1
    assert isinstance(result.exception, ValueError)
    assert 'Running in the same directory when no' in str(result.exception)


def test_get_dotfile_tree_valid_path(tmpdir):
    uid = str(uuid1())
    tmp = tmpdir.mkdir(uid)
    tmppath = str(tmp.realpath())
    runner = CliRunner()
    result = runner.invoke(
        filetree_digraph.get_dotfile_tree, ['-p', tmppath])
    assert result.exit_code == 0
    assert 'digraph' in result.output


def test_get_dotfile_tree_valid_path_dotfile(tmpdir):
    uid = str(uuid1())
    tmp = tmpdir.mkdir(uid)
    tmpfile = tmp.join('foo.dot')
    tmpfilepath = str(tmpfile.realpath())
    tmppath = str(tmp.realpath())
    runner = CliRunner()
    result = runner.invoke(
        filetree_digraph.get_dotfile_tree, ['-p', tmppath, '-d', tmpfilepath])
    assert result.exit_code == 0
    with open(tmpfilepath, 'r') as res:
        assert 'digraph' in str(res.read())
