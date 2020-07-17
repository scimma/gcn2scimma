#!/usr/bin/env bash

cd /install
pip3 install -e .
stream2hop tns --api_key {{secrets.API_Key}}