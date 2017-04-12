.PHONY: cleanpyc clean tests coverage dockerize help pypi testdata analysis
all: clean cleanpyc tests
analysis:
	prospector -s veryhigh flask_jsondash
clean:
	rm -rf coverage_report
cleanpyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
coverage: clean
	pytest -s -v --cov-report html --cov=flask_jsondash tests ; open coverage_report/index.html
dockerize:
	docker build --tag jsondash_base:latest -f BaseDockerfile .
	docker-compose build ; docker-compose up
pypi:
	python setup.py sdist upload -r pypi
sort:
	# https://github.com/timothycrosley/isort
	isort -rc flask_jsondash
tests:
	tox
testdata:
	python -m flask_jsondash.model_factories --records 10
help:
	@echo "all ......... Runs cleanup and tests"
	@echo "analysis .... Run prospector analysis"
	@echo "clean ....... Cleanup coverage"
	@echo "cleanpyc .... Remove .pyc files."
	@echo "coverage .... Generate coverage statistics and html"
	@echo "dockerize ... Setup docker containers and initialize example apps"
	@echo "tests ....... Run all tests"
	@echo "testdata .... Generate some test data"
