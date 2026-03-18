# pypaperless – Copilot Instructions

## Project Context

pypaperless is a Python client library for the Paperless-ngx REST API.
The library is structured around:

- `pypaperless/models/` — Pydantic models for API resources
- `pypaperless/services/` — Service classes with mixins (callable, iterable, securable, …)
- `tests/` — pytest unit tests with httpx mocking
- `script/pngx_smoketest.py` — live integration smoketest
- `script/pngx_audit_coverage.py` — field-level coverage audit against the live API schema

Live Paperless-ngx instance: `http://172.17.0.1:8000`
Auth token: `3e9505078d32d8ad4ecea00fa0eec8e426622b52`
Test document ID: `1980`
Dev venv: `/home/vscode/.local/dev-venv/bin/activate`

---

## Validation Policy

**After any code change, always run the full validation sequence before considering the task complete:**

**Exception:** for CLI-only changes limited to `pypaperless/cli.py` and/or CLI-focused tests/docs, the live smoketest is not required on every change.
In this case, run unit tests + coverage and report that the smoketest was intentionally skipped due to CLI-only scope.

1. **Unit tests + coverage**

   ```
   /usr/local/py-utils/bin/pytest -x -q
   ```

   Required: all tests green, coverage ≥ 95 %.

2. **Live smoketest**

   ```
   source /home/vscode/.local/dev-venv/bin/activate && python script/pngx_smoketest.py
   ```

   Required: 0 failures.

Report both results explicitly before closing the task.

---

## Suppression Policy

**`# noqa`, `# type: ignore`, and any other lint/type suppression comments are forbidden without explicit user confirmation — with one narrow exception.**

- Never add suppressions to work around a linting or type-checking issue.
- Always find a clean solution first (restructure the code, fix the type, adjust the import order, etc.).
- If no clean solution exists, **stop and ask the user** before adding a suppression — explain what the issue is and what the suppression would silence.
- This applies to all suppression forms: `# noqa`, `# noqa: <code>`, `# type: ignore`, `# type: ignore[<code>]`, `# pyright: ignore`, etc.

**Exception — pythonically idiomatic suppressions:** A suppression is permitted without confirmation only when it is the universally accepted Python/ecosystem convention for that exact pattern, and there is genuinely no cleaner alternative. Current recognised examples in this codebase:

- `# noqa: F401` on re-export lines in `__init__.py` files (the standard way to mark intentional public re-exports).

Any suppression not covered by an already-approved idiomatic pattern still requires explicit user confirmation.

---

## Code Conventions

- **Ruff compliance is mandatory for all newly generated code**: always follow the currently active Ruff rules/configuration in this repository when writing or modifying code.
- **Mypy compliance is mandatory for all newly generated code**: all new and modified code must type-check cleanly under the repository's active mypy configuration.
- Models use **Pydantic v2** (`BaseModel`, `model_validator`, `Field`).
- Services use **httpx** for async HTTP.
- Context managers (`@asynccontextmanager`) always use `try/finally` to guarantee cleanup.
- Public types are re-exported via `pypaperless/models/types.py`.
- Internal helpers are prefixed with `_` (e.g. `_PermissionScope`).
- When adding a new resource, follow the **add-resource** skill at `.github/skills/add-resource/SKILL.md`.
- When updating query filters (new/changed FilterSet fields in paperless-ngx), follow the **update-filters** skill at `.github/skills/update-filters/SKILL.md`.
