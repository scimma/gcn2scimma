##
## Install gcn2scimma
##
INSTALL_DIR   := /usr/local/gcn2hop
WORKING_DIR	  := ./gcn2hop
PYTHON_FILES  := gcn2hop,Utils.py
INSTALL_FILES := $(patsubst %,$(INSTALL_DIR)/%,$(PYTHON_FILES))
PYTHON = python

.PHONY: all install test

.PHONY: help
help :
	@echo
	@echo 'Commands:'
	@echo
	@echo '  make test                  run unit tests'
	@echo '  make lint                  run linter'
	@echo '  make format                run code formatter, giving a diff for recommended changes'
	@echo '  make doc                   make documentation'
	@echo '  make install				install module
	@echo

all:
	@echo No default make command. To install run "make install"

install:
	mkdir -p $(INSTALL_DIR)
	cp $(WORKING_DIR)/{$(PYTHON_FILES)} $(INSTALL_DIR)
	chmod ugo+rx $(WORKING_DIR)/{$(PYTHON_FILES)}

print-%  : ; @echo $* = $($*)

.PHONY: test
test :
	cd test && pytest -v

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
	black gcn2hop --diff