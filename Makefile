.PHONY: cleanpyc clean tests coverage dockerize help pypi testdata
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
pypi:
	python setup.py sdist upload -r pypi
sort:
	# https://github.com/timothycrosley/isort
	isort -rc flask_jsondash
testdata:
	python -m flask_jsondash.model_factories --records 10
help:
	@echo "all ......... Runs cleanup and tests"
	@echo "clean ....... Cleanup coverage"
	@echo "tests ....... Run all tests"
	@echo "coverage .... Generate coverage statistics and html"
	@echo "dockerize ... Setup docker containers and initialize example apps"
	@echo "cleanpyc .... Remove .pyc files."
	@echo "testdata .... Generate some test data"
