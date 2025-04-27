#
# To create a Python virtual environment, run:
#		python3 -m venv .venv;
#		source .venv/bin/activate;
#
.PHONY: help install lint test coverage

help:
	@cat ./Makefile

install:
	pip install -r requirements-dev.txt
	pre-commit install
	pre-commit install --hook-type commit-msg

lint:
	pylint $$(git ls-files '*.py')

test:
	python3 -m unittest discover tests

coverage:
	coverage run -m unittest discover tests && coverage report -m

git-hooks-test:
	pre-commit run --all-files
