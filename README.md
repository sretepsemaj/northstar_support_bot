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

This project expects a standard local Python environment:

- Python 3.x
- Python virtual environment support
- pip
- make

`make setup` runs a preflight check and prints Ubuntu/Debian install guidance if Python venv support is missing.

## Quick Start

From the project root:

```bash
make setup
make demo
```

Then open in your browser:

```text
http://localhost:8000
```

## Setup Details

`make setup` will first check that Python and venv support are available, then:

- Create a Python virtual environment at `.venv` if it does not exist
- Install dependencies from `requirements.txt`

Manual equivalent:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Run The App

```bash
make demo
```

This starts Uvicorn with:

```bash
.venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

## Run Tests

```bash
make test
```

Or directly:

```bash
.venv/bin/pytest
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
