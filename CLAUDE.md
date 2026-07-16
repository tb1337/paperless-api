# pypaperless – Claude Code Instructions

## Project

Python async client library for the Paperless-ngx REST API. Package manager: **uv**.

Public entry point: `PaperlessClient` (also exported: `PaperlessSettings`,
`generate_api_token`) — see `pypaperless/__init__.py`.

### Layout

- `pypaperless/` — library source
  - `models/` — Pydantic resource models (subpackages: `documents/`, `mails/`, `mixins/`,
    `permissions/`, `share_links/`, `workflows/`); public types re-exported via `models/types.py`;
    filter TypedDicts in `models/filters.py`
  - `services/` — API service classes composed from `services/mixins/` (`ResourceService` base
    in `services/base.py`)
  - `builders/` — fluent query builders (`search.py`, `custom_fields.py`)
  - top-level: `client.py`, `const.py`, `settings.py`, `transport.py`, `cache.py`,
    `dispatch.py`, `pagination.py`, `runtime.py`, `exceptions.py`, `utils.py`
- `tests/` — pytest + `pytest-httpx` mocks; fixture data per resource in `tests/data/`
- `script/` — `pngx_smoketest.py` (live smoketest), `pngx_audit_coverage.py` (API coverage
  audit), `pngx_fetch_schema.py` (refresh `tests/data/schema.json`)
- `docs/` — Markdown docs, built with `zensical` (`zensical.toml`)
- `run/debug.py` — local scratch/debug harness (not shipped)

### Current code surface (verify against these, not older docs)

`const.py` uses `EndpointPath(StrEnum)` (no `API_PATH` dict) · service base is
`ResourceService` / `PaperlessService` · mixins are `*Service` (`IterableService`,
`CallableService`, `CreatableService`, `UpdatableService`, `DeletableService`,
`SecurableService`) · runtime handle is `self._runtime` · services are registered lazily
via `@property`.

Live instance: `http://172.17.0.1:8000` · Token: `3e9505078d32d8ad4ecea00fa0eec8e426622b52` · Test doc: `1980`
Dev venv: `/home/vscode/.local/dev-venv/bin/activate`

It is fine to write IP and token here, they are both completely local and it is just a dev Paperless-ngx, without actual data, so what.

---

## Commands

```bash
uv sync                                   # install deps (add --group docs for docs)
uv run pytest -x -q                       # unit tests, coverage ≥ 95 %
uv run ruff check pypaperless             # lint (select = ALL)
uv run ruff format pypaperless            # format
uv run mypy                               # static type check (strict-ish)
uv run codespell                          # spell check
uv run yamllint .                         # YAML lint
prek run --all-files                      # run all pre-commit hooks
```

---

## Validation (always run after any code change)

```bash
uv run pytest -x -q                          # all green, coverage ≥ 95 %
uv run python script/pngx_smoketest.py       # 0 failures (needs live instance)
```

**Unit tests are always required.** The smoketest is only required when the change falls into
one of these categories:

- New service or model wired up (new API resource, new sub-service, new endpoint)
- Existing service/model/mixin behaviour changed in a way that could break live API interaction
- Changes to `client.py`, `const.py`, or `utils.py`

For everything else (docs, tests, filters, pure refactors, docstrings) — run unit tests only and
explicitly state that the smoketest was skipped and why.

Report both results (or the skip reason) before closing the task.

---

## Code Conventions

- Ruff (`select = ALL`) and mypy (strict-ish) must report **0 findings** on all new/modified code.
- Pydantic v2 (`BaseModel`, `model_validator`, `Field`) · httpx for async HTTP.
- `@asynccontextmanager` always uses `try/finally`.
- Public types re-exported via `pypaperless/models/types.py` · internal helpers prefixed with `_`.
- New resource → follow `.claude/skills/pp-add-resource/SKILL.md` (or invoke `/pp-add-resource`).
- Filter changes → follow `.claude/skills/pp-update-filters/SKILL.md` (or invoke `/pp-update-filters`).
- These skills are kept in sync with the current code surface (above); their snippets are the
  canonical templates.
- `# noqa`, `# type: ignore`, and all other suppression forms are **forbidden** — always fix the
  root cause; only `# noqa: F401` on re-export lines in `__init__.py` is allowed without asking.

---

## Docstring Conventions

### Public APIs

RST-style, one-line summary ending with a period, `Args:` (Google-style), `Example::`
(RST literal block). Every public symbol needs a usage example. Use Sphinx cross-references
for other library symbols. **No** Markdown fenced code blocks inside docstrings.

    def method(self, param: int) -> str:
        """One-line summary ending with a period.

        Args:
            param: What this parameter does.

        Example::

            result = await paperless.documents(42)
            print(result.title)

        """

Reference implementations: `pypaperless/builders/search.py`, `pypaperless/builders/custom_fields.py`.

### Private / internal APIs (`_` prefix or internal-only)

One- or two-line docstring only — focus on _why_ or non-obvious behaviour. No `Args:`, no example.

    def _get_document_pk(self, pk: int | None = None) -> int:
        """Return the attached document pk, or the parameter."""

## Good practices

- Keep comments concise. Prefer one short line stating the non-obvious constraint, or no comment at all.
- Do not add comments that just restate the code on the following line(s) (e.g. `# Check if initialized` above `if self.initialized:`). Comments should only explain why (non-obvious constraints, surprising behavior, or workarounds), never what. Never add comments that justify a change by referencing what the code looked like before.
- Do not add section or divider comments (e.g. `# --- XYZ Triggers ---`) inside or outside of functions, since those can easily become stale and be misleading.
- When catching exceptions, try-clauses should be as small as possible, i.e. avoid wrapping large blocks of code in a try-clause, and avoid catching exceptions from functions that are not expected to raise them.
