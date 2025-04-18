.PHONY: help lint test coverage

help:
	@cat ./Makefile

lint:
	pylint $$(git ls-files '*.py')

test:
	python3 -m unittest discover tests

coverage:
	coverage run -m unittest discover tests && coverage report -m
