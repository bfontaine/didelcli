.PHONY: all freeze check covercheck dist

SRC=didel

VENV=./venv
BINPREFIX=$(VENV)/bin/

PIP      = $(BINPREFIX)pip
COVERAGE = $(BINPREFIX)coverage

COVERFILE:=.coverage

PY_VERSION:=$(subst ., ,$(shell python --version 2>&1 | cut -d' ' -f2))
PY_VERSION_MAJOR:=$(word 1,$(PY_VERSION))
PY_VERSION_MINOR:=$(word 2,$(PY_VERSION))
PY_VERSION_SHORT:=$(PY_VERSION_MAJOR).$(PY_VERSION_MINOR)

ifdef TRAVIS_PYTHON_VERSION
PY_VERSION_SHORT:=$(TRAVIS_PYTHON_VERSION)
endif

deps: $(VENV)
	$(BINPREFIX)pip install -r requirements.txt
ifeq ($(PY_VERSION_SHORT),2.6)
	$(BINPREFIX)pip install unittest2 ordereddict
endif

freeze: $(VENV)
	$(PIP) freeze >| requirements.txt

$(VENV):
	virtualenv $@

clean-dist:
	$(RM) -r dist

# Tests

check:
	$(BINPREFIX)python tests/test.py

check-versions:
	$(BINPREFIX)tox

covercheck:
	$(COVERAGE) run --source=$(SRC) tests/test.py
	@# generate the CLI report
	$(COVERAGE) report -m
	@echo
	@# as well as the HTML one
	$(COVERAGE) html
	@echo '--> open htmlcov/index.html'

stylecheck:
	$(BINPREFIX)pyflakes didel

dist: deps clean-dist
	$(BINPREFIX)python setup.py sdist

publish: check-versions
	$(BINPREFIX)python setup.py sdist upload
