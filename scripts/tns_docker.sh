#!/usr/bin/env bash
###
### Run mi.sh in the scimma/base container.
###
docker run --rm -i -v `pwd`:/install  scimma/base:0.1.1 /install/scripts/tns_run.sh