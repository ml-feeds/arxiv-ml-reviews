.PHONY: help clean compile install test

help:
	@echo "clean  : Remove auto-created files and directories."
	@echo "compile: Compile required third-party Python packages."
	@echo "install: Install required third-party Python packages."
	@echo "test   : Run tests."

clean:
	rm -rf ./.*_cache

compile:
	pip-compile -U

install:
	pip install -U pip wheel
	pip install -U -r ./requirements.txt -U -r ./requirements-dev.in

test:
	mypy .
