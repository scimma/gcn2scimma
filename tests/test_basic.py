import os


def test_basic_gcn():
    cmd = "stream2hop gcn --help"
    ev = os.system(cmd)
    assert ev == 0


def test_basic_tns():
    cmd = "stream2hop tns --help"
    ev = os.system(cmd)
    assert ev == 0
