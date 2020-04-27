#!/usr/bin/env bash
###
### Run "make install" and "make test".
###
pip3 install pytest
cd /install
make install
make test
