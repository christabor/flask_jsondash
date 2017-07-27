.PHONY: cleanpyc cleanbuild clean tests coverage dockerize help pypi testdata analysis fixtures fixturize
all: clean cleanpyc cleanbuild tests
analysis:
	prospector -s veryhigh flask_jsondash
clean:
	rm -rf .tox/
	rm -rf coverage_report
cleanbuild:
	rm -rf build
	rm -rf dist
cleanpyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
coverage: clean
	pytest -s -v --cov-report html:coverage_report --cov=flask_jsondash tests ; open coverage_report/index.html
dockerize:
	docker build --tag jsondash_base:latest -f BaseDockerfile .
	docker-compose build ; docker-compose up
dropall:
	python -m flask_jsondash.model_factories --delete
fixtures:
	python -m flask_jsondash.model_factories --fixtures example_app/examples/config
fixturize:
	mkdir -p fixtures/
	python -m flask_jsondash.model_factories --dump fixtures
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
	@echo "cleanbuild .. Cleanup build and packaging related bits"
	@echo "cleanpyc .... Remove .pyc files."
	@echo "coverage .... Generate coverage statistics and html"
	@echo "dockerize ... Setup docker containers and initialize example apps"
	@echo "dropall ..... Delete all dashboards"
	@echo "fixtures .... Load all example dashboards"
	@echo "fixturize ... Convert existing database records to fixtures"
	@echo "tests ....... Run all tests"
	@echo "testdata .... Generate some test data"
