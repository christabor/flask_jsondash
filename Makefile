.PHONY: cleanpyc clean tests coverage dockerize
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
