#
# This file is for development usage only
#
# To create a Python virtual environment, run:
#		python3 -m venv .venv;
#		source .venv/bin/activate;
#
SHELL := /bin/bash
.PHONY: help install lint test coverage generate check-env install-ci test-ci coverage-ci lint-ci default
default: help

install-ci:
	pip install .[dev]

test-ci:
	python3 -m pytest

coverage-ci:
	python3 -m pytest --cov=drumgizmo_kits_generator --cov-report=xml

lint-ci: lint

## Verify that required commands are installed in the system
check-env:
	@${CHECK_CMD}; \
	check_command git; \
	check_command python3; \
	check_command pip; \
	check_command sox; \
	check_command diff;

## Install the app's dependencies & git hooks
install: check-env install-ci
	pre-commit install
	pre-commit install --hook-type commit-msg

## Format the code following the `.pre-commit-config.yaml` using `black` and `isort`
format:
	pre-commit run --hook-stage manual --show-diff-on-failure --color=always --all-files

## Run the linter with `pylint`
lint:
	pylint $$(git ls-files '*.py')

## Run the tests in `tests/` with `pytest`
test:
	python3 -m pytest -v

## Get the coverage analysis with `pytest`
coverage:
	python3 -m pytest --cov=drumgizmo_kits_generator --cov-report=term-missing

## Generate a test kit to `tests/target_test/` (excluded from VCS) from `examples/sources/` and compare it with `examples/target/`
generate:
	python3 create_drumgizmo_kit.py -s examples/sources/ -t tests/target_test/
	diff -r tests/target_test/ examples/target/ || true

## Cleanup Python's temporary files, cache and build
clean:
	find . \( \
		-name ".pytest_cache" \
		-o -name "__pycache__" \
		-o -name ".coverage" \
		-o -name "coverage.xml" \
		-o -name "*.pyc" \
		-o -name "build" \
	\) -exec rm -rf {} \;
	rm -rf tests/target_test

## Get the app's current version
version:
	@python3 create_drumgizmo_kit.py --app-version

## Run all checks: `format`, `lint`, `test`, `coverage` and `generate`
all: format lint test coverage generate

# This generates a 'help' string with the list of available tasks
# with their description if it is prefixed by two dashes:
#
#   ## This is a task comment
#   task_name: ...
#
# largely inspired by <https://docs.cloudposse.com/reference/best-practices/make-best-practices/>
help:
	@printf "This file is for development usage only\n"
	@printf "To use this file, run: make <target>\n"
	@printf "\n"
	@awk '/^[a-zA-Z0-9\-\\_\\]+:/ { \
		helpMessage = match(lastLine, /^## (.*)/); \
		if (helpMessage) { \
			helpCommand = $$1; \
			helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
			gsub("\\\\", "", helpCommand); \
			gsub(":+$$", "", helpCommand); \
			printf "  \x1b[32;01m%-15s\x1b[0m %s\n", helpCommand, helpMessage; \
		} \
	} \
	{ lastLine = $$0 }' $(MAKEFILE_LIST) | sort -u

RED = \033[0;31m
GREEN = \033[0;32m
NC = \033[0m
CHECK = \xE2\x9C\x94
CROSS = \xe2\x9c\x97
FAILURE = failure() { echo -e " ${RED}${CROSS} FAILED${NC} $$*"; }
SUCCESS = success() { echo -e " ${GREEN}${CHECK} OK${NC} $$*"; }
CHECK_CMD = check_command() { \
	${FAILURE}; ${SUCCESS}; \
	local _cmd=$$1; \
	echo -n "> checking if command is installed: '$$_cmd'"; \
	if ! command -v "$$_cmd" &> /dev/null; \
	then failure; \
	else success; \
	fi \
}
