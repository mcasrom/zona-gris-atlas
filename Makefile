PY := .venv/bin/python
PIP := .venv/bin/pip

.PHONY: setup lint test ingest classify export web serve backup

setup:
	python3 -m venv .venv
	$(PIP) install -e ".[dev]"

lint:
	.venv/bin/ruff check src tests scripts
	.venv/bin/bandit -q -r src

test:
	.venv/bin/pytest

ingest:
	$(PY) -m zonagris.cli ingest --source gdelt

classify:
	$(PY) -m zonagris.cli classify

export:
	$(PY) -m zonagris.cli export

web:
	$(PY) scripts/build_web.py
	$(PY) scripts/make_og.py

serve:
	$(PY) -m http.server -d web 8080

backup:
	./scripts/backup.sh
