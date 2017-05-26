import subprocess


def test_all_code_lints_via_prospector():
    res = subprocess.call(['prospector', '-s', 'veryhigh', 'flask_jsondash'])
    assert res == 0
