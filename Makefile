# This Makefile requires the following commands to be available:
# * python3.11

SRC:=pkgsettings tests setup.py

.PHONY: pyclean
pyclean:
	-find . -name "*.pyc" -delete
	-rm -rf *.egg-info build
	-rm -rf coverage*.xml .coverage

.PHONY: clean
clean: pyclean
	-rm -rf venv
	-rm -rf .tox

venv: PYTHON?=python3.11
venv:
	$(PYTHON) -m venv venv
	venv/bin/pip install -U pip -q
	venv/bin/pip install -r requirements.txt '.[all]'

## Code style
.PHONY: lint
lint: lint/black lint/flake8 lint/isort lint/mypy

.PHONY: lint/black
lint/black: venv
	venv/bin/black --diff --check $(SRC)

.PHONY: lint/flake8
lint/flake8: venv
	venv/bin/flake8 $(SRC)

.PHONY: lint/isort
lint/isort: venv
	venv/bin/isort --diff --check $(SRC)

.PHONY: lint/mypy
lint/mypy: venv
	venv/bin/mypy --python-version 3.7 -p pkgsettings -p tests
	venv/bin/mypy --python-version 3.8 -p pkgsettings -p tests
	venv/bin/mypy --python-version 3.9 -p pkgsettings -p tests
	venv/bin/mypy --python-version 3.10 -p pkgsettings -p tests
	venv/bin/mypy --python-version 3.11 -p pkgsettings -p tests

.PHONY: format
format: format/isort format/black

.PHONY: format/isort
format/isort: venv
	venv/bin/isort $(SRC)

.PHONY: format/black
format/black: venv
	venv/bin/black $(SRC)

## Tests
.PHONY: unittests
unittests: TOX_ENV?=ALL
unittests: TOX_EXTRA_PARAMS?=""
unittests: venv
	venv/bin/tox -e $(TOX_ENV) $(TOX_EXTRA_PARAMS)

.PHONY: test
test: pyclean unittests

## Distribution
.PHONY: changelog
changelog:
	venv/bin/gitchangelog

.PHONY: build
build: venv
	-rm -rf dist build
	venv/bin/python setup.py sdist bdist_wheel
	venv/bin/twine check dist/*
