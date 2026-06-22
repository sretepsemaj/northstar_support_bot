# Running Tests

Run tests from the project root, not from inside `backend/` or `tests/`.

Project root:

```bash
cd /Users/aaronjpeters/myprojects/UpWork/northstar_support_bot
```

## Run All Tests

```bash
.venv/bin/pytest
```

If pytest shows a local cache permission warning, run:

```bash
.venv/bin/pytest -p no:cacheprovider
```

## Run One Test File

```bash
.venv/bin/pytest tests/test_intent_service.py
```

Or with cache disabled:

```bash
.venv/bin/pytest tests/test_intent_service.py -p no:cacheprovider
```

## Run Tests By Keyword

```bash
.venv/bin/pytest -k intent
```

```bash
.venv/bin/pytest -k order
```

## Why Not Run Test Files With Python?

Do not run tests like this:

```bash
.venv/bin/python tests/test_intent_service.py
```

These files are pytest test modules. Running them directly can cause imports like `from backend...` to fail because Python may not load the project root the same way pytest does.

Use `pytest` from the project root instead.
