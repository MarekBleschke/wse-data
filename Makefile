.PHONY: clean clean-build clean-pyc clean-test coverage dist docs help install lint lint/flake8 lint/black
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-cache clean-test clean-dist ## remove all build, test, coverage and Python artifacts


clean-dist:  ## remove dist artifacts
	rm -fr dist/

clean-cache: ## remove mypy cache
	rm -fr .mypy_cache/

clean-test: ## remove test and coverage artifacts
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

lint/flake8: ## check style with flake8
	flake8 src
lint/black: ## check style with black
	black --check src
lint/mypy: ## check type annotations
	mypy --strict src

lint: lint/flake8 lint/black lint/mypy ## check style

test: ## run tests quickly with the default Python
	pytest --ignore=src/wse_data/tests/e2e

test-e2e: ## end to end tests
	pytest -v src/wse_data/tests/e2e

black: ## run black on sourcecode
	black src

coverage: ## check code coverage quickly with the default Python
	coverage run --source src -m pytest  --ignore=tests/e2e
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html
