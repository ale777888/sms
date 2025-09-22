VENV ?= .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
ARCHIVE ?= tg-sms.zip

.PHONY: bootstrap install bot admin package test clean

bootstrap install:
	bash scripts/bootstrap.sh

bot:
	bash scripts/run_bot.sh

admin:
	bash scripts/run_admin.sh

package:
	bash scripts/package.sh $(ARCHIVE)

test:
	$(PYTHON) -m pytest

clean:
	rm -rf $(VENV) data/*.db __pycache__ */__pycache__ .pytest_cache
