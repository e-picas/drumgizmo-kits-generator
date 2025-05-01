#
# To create a Python virtual environment, run:
#		python3 -m venv .venv;
#		source .venv/bin/activate;
#
.PHONY: help install lint test coverage
default: help

install-ci:
	pip install .[dev]

test-ci:
	python3 -m pytest

coverage-ci:
	coverage run -m unittest discover tests && coverage xml

lint-ci:
	pylint $$(git ls-files '*.py')

## Install the app's dependencies & git hooks
install: install-ci
	pre-commit install
	pre-commit install --hook-type commit-msg

## Format the code following the '.pre-commit-config.yaml'
format:
	pre-commit run --hook-stage manual --show-diff-on-failure --color=always --all-files

## Run the linter
lint:
	pylint $$(git ls-files '*.py')

## Run the tests
test:
	python3 -m pytest -v

## Get coverage info
coverage:
	coverage run -m unittest discover tests && coverage report -m

## Generate a test kit to `tests/target_test/`
generate:
	python create_drumgizmo_kit.py -s tests/sources/ -t tests/target_test/ -c tests/sources/drumgizmo-kit.ini

# This generates a 'help' string with the list of available tasks & variables
# in your Makefile(s) with their description if it is prefixed by two dashes:
#
#	## This is a variable
#	MY_VAR ?= my value
#
#   ## This is a task comment
#   task_name: ...
#
# largely inspired by <https://docs.cloudposse.com/reference/best-practices/make-best-practices/>
help:
	@printf "To use this file, run: make <target>\n"
	@printf "\n"
	@awk '/^[a-zA-Z0-9\-\\_\\]+:/ { \
		helpMessage = match(lastLine, /^## (.*)/); \
		if (helpMessage) { \
			helpCommand = $$1; \
			helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
			gsub("\\\\", "", helpCommand); \
			gsub(":+$$", "", helpCommand); \
			printf "  \x1b[32;01m%-20s\x1b[0m %s\n", helpCommand, helpMessage; \
		} \
	} \
	{ lastLine = $$0 }' $(MAKEFILE_LIST) | sort -u
	@printf "\n"
	@printf "To get a list of all available targets, you can use Make auto-completion: 'make <TAB><TAB>' or read the Makefile file.\n"
