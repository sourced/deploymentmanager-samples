PYTHON  ?= python
SHELL   := /bin/bash

help:
	@echo "cft-prerequisites         Installs prerequisites for CFT python utility development"
	@echo "cft-venv                  Creates the virtual environment called 'venv' for development"
	@echo "cft-clean-venv            Deletes the development environment"
	@echo "cft-test                  Runs all unit tests from outside of the venv (for CI tools)"
	@echo "cft-test-venv             Runs all unit tests from withing the venv (for active development)"
	@echo "template-prerequisites    Install prerequisites for template development"


.ONESHELL:
.PHONY: cft-prerequisites cft-venv cft-clean-venv cft-test cft-test-venv template-prerequisites

cft-prerequisites:
	${PYTHON} -m pip install -r requirements/utility-prerequisites.txt

cft-venv:
	${PYTHON} -m tox -e venv

cft-clean-venv:
	rm -rf venv

cft-test:
	${PYTHON} -m tox

cft-test-venv:
	${PYTHON} -m pytest -v

template-prerequisites:
	rm -rf bats && git clone https://github.com/sstephenson/bats.git && ./bats/install.sh ../venv && rm -rf bats
