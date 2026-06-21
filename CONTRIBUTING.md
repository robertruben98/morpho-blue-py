# Contributing

Thanks for your interest in improving **morpho-blue-py**! This guide covers the
local setup and the checks your change needs to pass.

## Development setup

The project uses [uv](https://docs.astral.sh/uv/), but plain `pip` works too.

```bash
# with uv (recommended)
uv venv --python 3.9
uv pip install -e ".[dev]"

# or with pip
python -m venv .venv && source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

We target **Python 3.9+**, so develop against 3.9 when in doubt. Runtime-evaluated
type annotations (e.g. inside pydantic models) must avoid PEP 604 `X | None` —
use `typing.Optional`/`typing.Union` instead.

## Quality gates

All of these must be green before a PR can merge; CI runs them on Python
3.9–3.13.

```bash
ruff check .            # lint
mypy                    # type-check (strict)
pytest                  # unit tests (no network)
```

Unit tests must not hit the network — they use `respx` with realistic GraphQL
fixtures (see `tests/fixtures.py`). The single live test is marked `integration`
and deselected by default; run it explicitly with:

```bash
pytest -m integration
```

## Workflow

1. Branch off `main`.
2. Follow test-driven development: add a failing test, then the implementation.
3. Keep public APIs documented with Google-style docstrings and pydantic
   `Field(description=...)`.
4. Update `CHANGELOG.md` under `[Unreleased]`.
5. Open a pull request; ensure CI is green.

## Reporting issues

Please file bugs and feature requests at
<https://github.com/robertruben98/morpho-blue-py/issues>.
