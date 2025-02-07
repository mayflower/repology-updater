FLAKE8?=	flake8
MYPY?=		mypy

REPOLOGY_TEST_DUMP_PATH?=	.

lint:: check test flake8 mypy

test::
	python3 -m unittest discover

test-make-dump::
	env REPOLOGY_CONFIG=./repology-test.conf.default ./repology-update.py -ippd
	pg_dump -U repology_test -c \
		| grep -v '^CREATE EXTENSION' \
		| grep -v '^COMMENT ON EXTENSION' \
		| grep -v '^DROP EXTENSION' \
		> ${REPOLOGY_TEST_DUMP_PATH}/repology_test.sql

flake8:
	${FLAKE8} --application-import-names=repology *.py repology

mypy:
	${MYPY} *.py repology
	${MYPY} repology/fetchers/fetchers
	${MYPY} repology/parsers/parsers

check:
	python3 repology-schemacheck.py -s repos $$(find repos.d -name "*.yaml")
