from uuid import uuid1

import pytest

from flask_jsondash.data_utils import filetree_digraph


def test_make_dotfile(tmpdir):
    uid = uuid1()
    dirname = '{}'.format(uid)
    tmp = tmpdir.mkdir(dirname)
    for i in range(10):
        tmp.join('{}.txt'.format(i)).write('{}'.format(i))
    data = filetree_digraph.make_dotfile(tmp.strpath)
    # Ensure wrapping lines are proper digraph format.
    assert data.startswith('digraph {\n')
    assert data.endswith('\n}\n')
    lines = data.split('\n')
    # Ensure each line has the right dotfile format.
    for i, line in enumerate(lines[1:len(lines) - 2]):
        assert line == '\t"{0}" -> "{1}.txt";'.format(uid, i)


def test_make_dotfile_invalid_path(tmpdir):
    with pytest.raises(OSError):
        filetree_digraph.make_dotfile('invalid-path')
