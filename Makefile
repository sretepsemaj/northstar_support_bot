.PHONY: preflight setup demo test clean

preflight:
	@command -v python3 >/dev/null 2>&1 || { \
		echo "Python 3 is required but was not found."; \
		echo "Install Python 3, then rerun:"; \
		echo "  make setup"; \
		exit 1; \
	}
	@python3 -c "import venv" >/dev/null 2>&1 || { \
		echo "Python venv support is missing."; \
		echo "Install Python virtual environment support for your operating system, then retry:"; \
		echo "  rm -rf .venv"; \
		echo "  make setup"; \
		echo "On Ubuntu/Debian, this is usually:"; \
		echo "  sudo apt update"; \
		echo "  sudo apt install -y python3-venv python3-pip make"; \
		echo "If your system uses Python 3.12 packages:"; \
		echo "  sudo apt install -y python3.12-venv python3-pip make"; \
		exit 1; \
	}
	@tmp_dir=$$(mktemp -d 2>/dev/null || mktemp -d -t northstar-venv); \
	if ! python3 -m venv "$$tmp_dir" >/dev/null 2>&1; then \
		rm -rf "$$tmp_dir"; \
		echo "Python virtual environment creation failed."; \
		echo "Install Python virtual environment support for your operating system, then retry:"; \
		echo "  rm -rf .venv"; \
		echo "  make setup"; \
		echo "On Ubuntu/Debian, this is usually:"; \
		echo "  sudo apt update"; \
		echo "  sudo apt install -y python3-venv python3-pip make"; \
		echo "If your system uses Python 3.12 packages:"; \
		echo "  sudo apt install -y python3.12-venv python3-pip make"; \
		exit 1; \
	fi; \
	rm -rf "$$tmp_dir"

setup: preflight
	@if [ ! -d .venv ]; then python3 -m venv .venv; fi
	.venv/bin/pip install -r requirements.txt

demo:
	.venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000

test:
	.venv/bin/pytest

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	rm -rf .pytest_cache
