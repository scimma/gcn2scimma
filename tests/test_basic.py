import os


def test_basic():
    cmd = "gcn2hop --help"
    ev = os.system(cmd)
    assert ev == 0
