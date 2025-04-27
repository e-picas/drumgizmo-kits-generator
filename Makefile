#
# To create a Python virtual environment, run:
#		python3 -m venv .venv;
#		source .venv/bin/activate;
#
.PHONY: help install lint test coverage

help:
	@cat ./Makefile

install-ci:
	pip install -r requirements-dev.txt

install: install-ci
	pre-commit install
	pre-commit install --hook-type commit-msg

lint:
	pylint $$(git ls-files '*.py')

test:
	python3 -m unittest discover tests

coverage:
	coverage run -m unittest discover tests && coverage report -m

pre-commit-run:
	pre-commit run --hook-stage manual --show-diff-on-failure --color=always --all-files
