from uuid import uuid1

import pytest

from click.testing import CliRunner

from flask_jsondash.data_utils import filetree_digraph


def test_make_dotfile(tmpdir):
    tmp = tmpdir.mkdir('somedir')
    for i in range(4):
        tmp.join('{}.txt'.format(i)).write('{}'.format(i))
    data = filetree_digraph.make_dotfile(tmp.strpath)
    # Ensure wrapping lines are proper digraph format.
    res = data.split('\n')
    assert res[0] == 'digraph {'
    assert res[1] == '\t"somedir" -> "0.txt";'
    assert res[2] == '\t"somedir" -> "1.txt";'
    assert res[3] == '\t"somedir" -> "2.txt";'
    assert res[4] == '\t"somedir" -> "3.txt";'
    assert res[5] == '}'


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
    runner = CliRunner()
    result = runner.invoke(
        filetree_digraph.get_dotfile_tree, ['-p', tmp.strpath, '-d',
                                            tmpfilepath])
    assert result.exit_code == 0
    with open(tmpfilepath, 'r') as res:
        assert 'digraph' in res.read()
