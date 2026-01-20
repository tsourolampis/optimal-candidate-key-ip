# Makefile
# Usage: make test

PYTHON := python3
VENV   := .venv
PIP    := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest

.PHONY: test

test:
	@set -e; \
	if [ ! -x "$(PIP)" ]; then \
		$(PYTHON) -m venv $(VENV); \
		$(PIP) install --upgrade pip setuptools wheel; \
	fi; \
	$(PIP) install -e ".[dev]"; \
	$(PYTEST) -q -v
