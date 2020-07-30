#!/bin/bash
###
### Author: rdt12@psu.edu
### Date:   Apr 24, 2020
### Desc:   Use the current AWS credentials to login to the AWS ECR using docker.
###         Note that aws and docker must be in your PATH.
###
REGION=$1
REGISTRY=$2
if [ -z "$REGION" ]; then
  echo "No region specified."
  exit -1
fi
if [ -z "$REGISTRY" ]; then
    echo "No registry specified."
    exit -1
fi
aws ecr get-login-password --region "$REGION" | docker login -u AWS --password-stdin "$REGISTRY"