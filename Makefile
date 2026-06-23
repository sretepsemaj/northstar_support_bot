.PHONY: setup setup-uv demo demo-uv test test-uv clean doctor

setup:
	@command -v python3 >/dev/null 2>&1 || { \
		echo "Python 3 is required. See README.md Prerequisites."; \
		exit 1; \
	}
	@if [ ! -x .venv/bin/pip ]; then \
		python3 -m venv .venv || { \
			echo ""; \
			echo "Could not create .venv."; \
			echo "Your system Python may be missing venv/ensurepip support."; \
			echo ""; \
			echo "On Ubuntu/Debian, run:"; \
			echo "  sudo apt update && sudo apt install -y python3 python3-venv python3-pip make"; \
			echo "  rm -rf .venv && make setup"; \
			echo ""; \
			echo "If sudo is not available but uv is installed, run:"; \
			echo "  rm -rf .venv && make setup-uv"; \
			exit 1; \
		}; \
	fi
	.venv/bin/pip install -r requirements.txt

setup-uv:
	@command -v uv >/dev/null 2>&1 || { \
		echo "uv is required for setup-uv. Install uv or use make setup."; \
		exit 1; \
	}
	@if [ ! -x .venv/bin/python ]; then uv venv .venv; fi
	uv pip install --python .venv/bin/python -r requirements.txt

demo:
	.venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000

demo-uv:
	.venv/bin/python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

test:
	.venv/bin/pytest

test-uv:
	.venv/bin/python -m pytest

doctor:
	@echo "Checking startup prerequisites..."
	@command -v python3 >/dev/null 2>&1 && echo "python3: OK" || echo "python3: MISSING"
	@command -v make >/dev/null 2>&1 && echo "make: OK" || echo "make: MISSING"
	@tmp_dir=$$(mktemp -d 2>/dev/null || mktemp -d -t northstar-venv); \
	python3 -m venv "$$tmp_dir" >/dev/null 2>&1 && echo "venv: OK" || echo "venv: FAIL"; \
	rm -rf "$$tmp_dir"
	@command -v uv >/dev/null 2>&1 && echo "uv: AVAILABLE (fallback option)" || echo "uv: not found"

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	rm -rf .pytest_cache
