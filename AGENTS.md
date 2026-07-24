# AGENTS.md

Guidance for AI coding agents working in this repo.

## Project overview

Async Python client library for the Paperless-ngx REST API. Package manager: **uv**.

Public entry point: `PaperlessClient` (also exported: `PaperlessSettings`, `generate_api_token`) —
see `pypaperless/__init__.py`.

- `pypaperless/` — library source
  - `models/` — Pydantic v2 resource models (subpackages `documents/`, `mails/`, `mixins/`,
    `permissions/`, `share_links/`, `workflows/`); public types re-exported via `models/types.py`;
    filter TypedDicts in `models/filters.py`
  - `services/` — API service classes composed from `services/mixins/` (base `ResourceService` in
    `services/base.py`); registered lazily via `@property`
  - `builders/` — fluent query builders (`search.py`, `custom_fields.py`)
  - top-level: `client.py`, `const.py`, `settings.py`, `transport.py`, `cache.py`, `dispatch.py`,
    `pagination.py`, `runtime.py`, `exceptions.py`, `utils.py`
- `tests/` — pytest + `pytest-httpx`; fixture data per resource in `tests/data/`
- `script/` — `pngx_smoketest.py` (live smoketest), `pngx_audit_coverage.py` (API coverage audit),
  `pngx_fetch_schema.py` (refresh `tests/data/schema.json`)
- `docs/` — Markdown, built with `zensical`

Current code surface (trust these over older docs): `const.py` uses `EndpointPath(StrEnum)` (no
`API_PATH` dict) · service base `ResourceService` / `PaperlessService` · mixins are `*Service`
(`Iterable`, `Callable`, `Creatable`, `Updatable`, `Deletable`, `Securable`) · runtime handle
`self._runtime`.

## Dev Commands

- `uv sync` — install deps (add `--group docs` for docs)
- `uv run pytest -x -q` — unit tests, coverage ≥ 95 %
- `uv run ruff check pypaperless` — lint (`select = ALL`)
- `uv run ruff format pypaperless` — format
- `uv run mypy` — static type check (strict-ish)
- `uv run codespell` — spell check
- `uv run yamllint .` — lint YAML (enforced by pre-commit)
- `prek run --all-files` — all pre-commit hooks

Local dev instance credentials live in the git-ignored `.env`
(`PYPAPERLESS_URL`, `PYPAPERLESS_TOKEN`, `PYPAPERLESS_TEST_DOC`) — copy `.env.example` to `.env`.
Activate the dev venv before running scripts. The `script/*.py` tools and `run/debug.py` read the
`.env` via `script/_dev_env.py`.

## Testing instructions

1. `uv run pytest -x -q` — always required, all green, coverage ≥ 95 %.
2. `uv run python script/pngx_smoketest.py` — **only** when the change could affect live API
   interaction: new/changed service, model, mixin or endpoint, or edits to `client.py`, `const.py`,
   `utils.py`. Needs a live instance (below); expect 0 failures.

For docs, filters, pure refactors and docstrings, run unit tests only and state that the smoketest
was skipped and why. Report both results (or the skip reason) before closing the task.

## PR instructions

- Branch off `main`; keep the branch scoped to one logical change.
- Title format: `<type>: <summary>` (e.g. `fix:`, `feat:`, `docs:`, `refactor:`).
- Before opening a PR, all `## Dev Commands` pass and the `## Testing instructions` are satisfied
  (report the smoketest result or the skip reason).
- Fill in the PR template and do not uncheck/remove its checkboxes.

## Code style

- Ruff (`select = ALL`) and mypy must report **0 findings** on new/modified code.
- `# noqa`, `# type: ignore` and all other suppressions are **forbidden** — fix the root cause.
  Only `# noqa: F401` on re-export lines in `__init__.py` is allowed without asking.
- Pydantic v2 (`BaseModel`, `model_validator`, `Field`) · httpx for async HTTP.
- `@asynccontextmanager` always uses `try/finally`.
- Public types re-exported via `models/types.py`; internal helpers prefixed with `_`.
- New resource → `.claude/skills/pp-add-resource/SKILL.md` (or `/pp-add-resource`).
  Filter changes → `.claude/skills/pp-update-filters/SKILL.md` (or `/pp-update-filters`).
  These skills track the current code surface and hold the canonical templates.

## Good practices

- Comments explain *why* (non-obvious constraints, surprises, workarounds), never *what*. Prefer
  one short line, or none. Never justify a change by referencing what the code used to be.
- No section/divider comments (e.g. `# --- Triggers ---`) — they go stale.
- Keep try-clauses minimal: wrap only the statement that can raise, catch only expected exceptions.
- Docstrings: public APIs RST-style (one-line summary, Google `Args:`, mandatory `Example::` block, no Markdown fences — see `pypaperless/builders/search.py`); private `_` symbols one or two lines on *why* only.
