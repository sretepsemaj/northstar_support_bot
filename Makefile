.PHONY: setup demo test clean

setup:
	@if [ ! -d .venv ]; then python3 -m venv .venv; fi
	.venv/bin/pip install -r requirements.txt

demo:
	.venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000

test:
	.venv/bin/pytest

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	rm -rf .pytest_cache
