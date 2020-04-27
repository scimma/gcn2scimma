#!/usr/bin/env bash
###
### Run "make install" and "make test".
###
pip3 install pytest
cd /install
pip3 install -r requirements.txt
make install
make test
