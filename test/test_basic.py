import os

def test_basic ():
    cmd = "/usr/local/gcn2hop --help"
    ev = os.system(cmd)
    assert(ev == 0)
