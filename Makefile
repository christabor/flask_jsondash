.PHONY: cleanpyc clean tests coverage dockerize help
all: clean cleanpyc tests
clean:
	rm -rf coverage_report
tests:
	tox
coverage: clean
	pytest -s -v --cov-report html --cov=flask_jsondash tests
dockerize:
	docker build --tag jsondash_base:latest -f BaseDockerfile .
	docker-compose build ; docker-compose up
cleanpyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
help:
	@echo "all ......... Runs cleanup and tests"
	@echo "clean ....... Cleanup coverage"
	@echo "tests ....... Run all tests"
	@echo "coverage .... Generate coverage statistics and html"
	@echo "dockerize ... Setup docker containers and initialize example apps"
	@echo "cleanpyc .... Remove .pyc files."
