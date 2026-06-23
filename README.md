# North Star Support Bot

A FastAPI customer support chatbot demo for a fictional outdoor apparel and camping gear e-commerce business.

This project was built for the Upwork Talent Accelerator simulated chatbot assignment. It focuses on clear conversation flows, deterministic mock data handling, practical test coverage, and an optional LLM-assisted intent review layer.

## Core Use Cases

The bot handles the required support scenarios:

- Order Tracking
- Returns & Exchanges
- Product Recommendations
- Human Handoff
- Fallback Handling
- Gratitude

## Prerequisites

This project needs Python 3. The recommended local setup uses `make` for short commands.

Project dependencies install into a local `.venv/` folder inside this repo. Deleting the project folder also removes the project dependencies.

## Quick Start

From the repo root:

```bash
make setup
make demo
```

Then open:

```text
http://localhost:8000
```

Run tests with:

```bash
make test
```

## What Success Looks Like

A successful startup should:

- Create a local `.venv/` directory
- Install dependencies from `requirements.txt`
- Start Uvicorn on port `8000`

After startup:

- `http://localhost:8000` loads the demo UI
- `http://localhost:8000/health` returns JSON with `"status": "ok"`

## Setup Troubleshooting

If you want a quick environment check, run:

```bash
make doctor
```

## Manual Setup Without make: macOS/Linux

Use this if `make` is not available:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Run tests with:

```bash
.venv/bin/python -m pytest
```

## Windows PowerShell

Windows usually uses `python` instead of `python3`. If Python was just installed, reopen PowerShell before running setup.

```powershell
winget install Python.Python.3.12
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Run tests with:

```powershell
.\.venv\Scripts\python -m pytest
```

## VPS With Sudo

If `make setup` fails while creating `.venv`, your system Python may be missing virtual environment support. On Ubuntu/Debian, run:

```bash
sudo apt update && sudo apt install -y python3 python3-venv python3-pip make
rm -rf .venv
make setup
make demo
```

If your Linux system uses Python 3.12-specific packages, use:

```bash
sudo apt update && sudo apt install -y python3.12-venv python3-pip make
rm -rf .venv
make setup
make demo
```

## No-Sudo Fallback With uv

If system Python cannot create a virtual environment and you already have `uv` installed, you can run the project without sudo:

```bash
uv venv .venv
uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Run tests with:

```bash
.venv/bin/python -m pytest
```

## Environment Variables

Copy `.env.example` to `.env` if you want local configuration:

```bash
cp .env.example .env
```

Default behavior does not require an API key.

```env
USE_LLM=false
LLM_PROVIDER=
LLM_MODEL=
LLM_API_KEY=
```

Optional OpenAI-compatible LLM mode can be enabled locally:

```env
USE_LLM=true
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
LLM_API_KEY=your_local_key_here
```

Do not commit `.env`. It is intentionally ignored by git.

## LLM Design

The chatbot works without an LLM.

When enabled, the LLM is used only as a lightweight classifier for ambiguous messages. The application still controls final responses, allowed categories, order data, return policy, and handoff behavior.

This keeps token usage low and prevents unsupported product or policy claims.

## Mock Data

Order tracking uses the assignment-provided mock logic:

```text
Order #111 -> Shipped, arriving tomorrow
Order #222 -> Processing, ships in 24 hours
Order #333 -> Delivered, asks follow-up if needed
Any other order -> Invalid order
```

Returns use the provided policy:

```text
30-day returns, unused items, original packaging
```

## Project Structure

```text
backend/
  api/routes/       FastAPI route handlers
  chatbot/          Conversation flow and response helpers
  core/             App configuration
  data/             Mock business data
  schemas/          Request/response schemas
  services/         Intent, chat, order, returns, recommendation, handoff, LLM services
frontend/
  index.html        The mock home page
  css/              Demo page and support widget styling
  js/               Widget, API, rendering, and scenario logic
tests/              Unit and API tests
```

## Notes

- No deployment is required.
- No Docker or npm setup is required.
- The app uses provided mock data only.
- The demo UI is intentionally simple: it shows how the support widget can be embedded on a customer page. The small demo tracker helps reviewers see which required scenarios have been demonstrated during the walkthrough.
