.PHONY: help lint test

help:
	@cat ./Makefile

lint:
	pylint $$(git ls-files '*.py')

test:
	python3 -m unittest discover tests
