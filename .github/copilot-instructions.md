# pypaperless – Copilot Instructions

## Project

Python async client library for the Paperless-ngx REST API.

- `pypaperless/models/` — Pydantic models · `pypaperless/services/` — service classes + mixins
- `tests/` — pytest + httpx mocks · `script/pngx_smoketest.py` — live smoketest · `script/pngx_audit_coverage.py` — API coverage audit

Live instance: `http://172.17.0.1:8000` · Token: `3e9505078d32d8ad4ecea00fa0eec8e426622b52` · Test doc: `1980`
Dev venv: `/home/vscode/.local/dev-venv/bin/activate`

---

## Validation (always run after any code change)

```
/usr/local/py-utils/bin/pytest -x -q                                                  # all green, coverage ≥ 95 %
source /home/vscode/.local/dev-venv/bin/activate && python script/pngx_smoketest.py  # 0 failures
```

**Unit tests are always required.** The smoketest is only required when the change falls into one of these categories:

- New service or model wired up (new API resource, new sub-service, new endpoint)
- Existing service/model/mixin behaviour changed in a way that could break live API interaction
- Changes to `client.py`, `const.py`, or `utils.py`

For everything else (docs, tests, filters, pure refactors, docstrings) — run unit tests only and explicitly state that the smoketest was skipped and why.

Report both results (or the skip reason) before closing the task.

---

## Code Conventions

- Ruff (`select = ALL`) and mypy (strict-ish) must report **0 findings** on all new/modified code.
- Pydantic v2 (`BaseModel`, `model_validator`, `Field`) · httpx for async HTTP.
- `@asynccontextmanager` always uses `try/finally`.
- Public types re-exported via `pypaperless/models/types.py` · internal helpers prefixed with `_`.
- New resource → follow `.github/skills/add-resource/SKILL.md`.
- Filter changes → follow `.github/skills/update-filters/SKILL.md`.
- `# noqa`, `# type: ignore`, and all other suppression forms are **forbidden** — always fix the root cause; only `# noqa: F401` on re-export lines in `__init__.py` is allowed without asking.

---

## Docstring Conventions

### Public APIs

RST-style, one-line summary ending with a period, `Args:` (Google-style), `Example::` (RST literal block).
Every public symbol needs a usage example. Use Sphinx cross-references for other library symbols.
**No** Markdown fenced code blocks inside docstrings.

```python
def method(self, param: int) -> str:
    """One-line summary ending with a period.

    Args:
        param: What this parameter does.

    Example::

        result = await paperless.documents(42)
        print(result.title)

    """
```

Reference implementations: `pypaperless/builders/search.py`, `pypaperless/builders/custom_fields.py`.

### Private / internal APIs (`_` prefix or internal-only)

One- or two-line docstring only — focus on _why_ or non-obvious behaviour. No `Args:`, no example.

```python
def _get_document_pk(self, pk: int | None = None) -> int:
    """Return the attached document pk, or the parameter."""
```
