.PHONY : test-local test-local-file serve build-docs check-readme install-local lint format dev-setup

check-readme:
	rm -rf dist build django_graphql_auth.egg-info
	python setup.py sdist bdist_wheel
	python -m twine check dist/*

install-local:
	rm -rf dist build django_graphql_auth.egg-info
	python setup.py sdist bdist_wheel
	python -m pip install dist/django-graphql-auth-${v}.tar.gz

python ?= 38
django ?= 3

test:
	tox -e py${python}-django${django} -- --cov-report term-missing --cov-report html

test-file:
	tox -e py${python}-django${django} -- tests/test_${f}.py --cov-report html --cov-append

serve:
	python docs/pre_build.py
	mkdocs serve

build-docs:
	python docs/pre_build.py
	mkdocs build

format:
	black --exclude "/migrations/" graphql_auth testproject setup.py quickstart tests

lint:
	flake8 graphql_auth

dev-setup:
	pip install -e ".[dev]"
