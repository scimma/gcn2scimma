
PYTHON = python

CNT_NAME := scimma/tns2hop

TAG      := $(shell git log -1 --pretty=%H || echo MISSING )
CNT_IMG  := $(CNT_NAME):$(TAG)
CNT_LTST := $(CNT_NAME):latest

REGION  := us-west-2
AWSREG  := 585193511743.dkr.ecr.us-west-2.amazonaws.com
MAJOR   := 0
MINOR   := 0
RELEASE := 4
DOCKERFILE := dockerfile

RELEASE_TAG := $(MAJOR).$(MINOR).$(RELEASE)

.PHONY: all install test set-release-tags docker_push clean tns_container

.PHONY: help
help :
	@echo
	@echo 'Commands:'
	@echo
	@echo '  make test                  run unit tests'
	@echo '  make lint                  run linter'
	@echo '  make format                run code formatter, giving a diff for recommended changes'
	@echo '  make doc                   make documentation'
	@echo '  make install		    install module
	@echo

all:
	@echo No default make command. To install run "make install"

install:
	$(PYTHON) setup.py install

print-%  : ; @echo $* = $($*)

.PHONY: test
test :
	cd tests && pytest -v

.PHONY: clean
clean :
	rm -f *~
	rm -rf __pycache__

.PHONY: lint
lint :
	# stop the build if there are Python syntax errors or undefined names
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	# exit-zero treats all errors as warnings
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=100 --statistics

.PHONY: format
format :
	# show diff via black
	black tests --diff
	black stream2hop --diff

print-%  : ; @echo $* = $($*)


.PHONY: tns_container
tns_container: 
	@if [ ! -z "$$(git status --porcelain)" ]; then echo "Directory is not clean. Commit your changes."; exit 1; fi
	docker build -f Dockerfile_TNS -t $(CNT_IMG) .
	docker tag $(CNT_IMG) $(CNT_LTST)

.PHONY: set-release-tags
set-release-tags:
	@$(eval RELEASE_TAG := $(shell echo $(GITHUB_REF) | awk -F- '{print $$2}'))
	@echo RELEASE_TAG =  $(RELEASE_TAG)
	@$(eval MAJOR_TAG   := $(shell echo $(RELEASE_TAG) | awk -F. '{print $$1}'))
	@echo MAJOR_TAG = $(MAJOR_TAG)
	@$(eval MINOR_TAG   := $(shell echo $(RELEASE_TAG) | awk -F. '{print $$2}'))
	@echo MINOR_TAG = $(MINOR_TAG)

.PHONY: docker_push
docker_push: 
	./scrips/awsDockerLogin $(REGION) $(AWSREG) >/dev/null 2>/dev/null
	docker tag $(CNT_IMG) $(AWSREG)/$(CNT_NAME):$(RELEASE_TAG)
	docker tag $(CNT_IMG) $(AWSREG)/$(CNT_NAME):$(MAJOR)
	docker tag $(CNT_IMG) $(AWSREG)/$(CNT_NAME):$(MAJOR).$(MINOR)
	docker push $(AWSREG)/$(CNT_NAME):$(RELEASE_TAG)
	docker push $(AWSREG)/$(CNT_NAME):$(MAJOR)
	docker push $(AWSREG)/$(CNT_NAME):$(MAJOR).$(MINOR)
#	rm -f $(HOME)/.docker/config.json

.PHONY: clean
clean:
	rm -f *~
	rm -f downloads/*
	if [ -d downloads ]; then  rmdir downloads else /bin/true; fi