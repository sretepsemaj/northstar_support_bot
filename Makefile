.PHONY: setup run test clean

setup:
	@if [ ! -d .venv ]; then python3 -m venv .venv; fi
	.venv/bin/pip install -r requirements.txt

run:
	.venv/bin/python backend/main.py

test:
	.venv/bin/pytest

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	rm -rf .pytest_cache
