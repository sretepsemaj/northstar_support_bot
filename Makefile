.PHONY: setup demo test clean

setup:
	@command -v python3 >/dev/null 2>&1 || { \
		echo "Python 3 is required. See README.md Prerequisites."; \
		exit 1; \
	}
	@if [ ! -x .venv/bin/pip ]; then \
		python3 -m venv .venv || { \
			echo "Could not create .venv. See README.md Prerequisites, then retry: rm -rf .venv && make setup"; \
			exit 1; \
		}; \
	fi
	.venv/bin/pip install -r requirements.txt

demo:
	.venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000

test:
	.venv/bin/pytest

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	rm -rf .pytest_cache
