# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`pypaperless` is a fully async Python client library for the [Paperless-ngx](https://docs.paperless-ngx.com/) REST API. Built on `httpx.AsyncClient` + Pydantic v2, targeting Python 3.13+ (also tested on 3.14). Build backend is hatchling; dependencies are managed with `uv`.

## Common commands

All commands run via `uv` (dev venv is created by `script/bootstrap`):

```bash
# One-time setup (creates .venv, installs deps, installs prek hooks)
script/setup

# Test suite (coverage ≥ 95 % is enforced via covdefaults / pyproject.toml)
uv run pytest                                # full run with coverage
uv run pytest -x -q                          # fast fail-fast unit run
uv run pytest tests/test_documents.py        # single file
uv run pytest tests/test_documents.py -k name_of_test   # single test

# Linting / formatting / typing (must report 0 findings on changed code)
uv run ruff check --fix
uv run ruff format
uv run mypy

# YAML + spelling (also run by prek hooks)
uv run yamllint .
uv run codespell

# Run all pre-commit hooks against the working tree
uv run prek run --all-files
```

The codebase declares `--cov` in `[tool.pytest.ini_options]`, so `pytest` always produces coverage. `pytest-asyncio` is in auto mode (no `@pytest.mark.asyncio` needed).

### Live-instance scripts (require a running Paperless-ngx)

```bash
uv run python script/pngx_fetch_schema.py     # refresh tests/data/schema.json from a live host
uv run python script/pngx_smoketest.py        # hit a live host across all services
uv run python script/pngx_audit_coverage.py   # diff implemented endpoints vs. live OpenAPI schema
```

Smoketest is only required when wiring up a new service/model, changing a service/model/mixin in a way that could break live calls, or touching `client.py` / `const.py` / `utils.py`. For docs, tests, filters, and pure refactors, run unit tests only and state the smoketest was skipped.

## Architecture

The library is layered: **client → runtime (transport + cache) → services → models**. A small dispatcher decouples model operations from services so callers can write `await paperless.update(doc)` without knowing which service owns `Document`.

### Object graph

- **`PaperlessClient`** (`pypaperless/client.py`) — public entry point. Async context manager that calls `initialize()` (probes `/api/schema/` for `x-api-version` / `x-version`) and `close()`. Exposes every service as a `@cached_property` or `@dispatchable_cached_property`. `from_config(PaperlessSettings)` and `from_env()` are alternative constructors.
- **`PaperlessRuntime`** (`runtime.py`) — small container of `transport` + `cache` + `api_version`. Every service receives the runtime in its constructor; never instantiate services with a `PaperlessClient` directly.
- **`PaperlessTransport`** (`transport.py`) — wraps an `httpx.AsyncClient`. Adds `Authorization: Token …`, version-aware `Accept` header, translates 401/403 into typed exceptions (`InvalidTokenError`, `InactiveOrDeletedError`, `ForbiddenError`), and parses JSON / raises `BadJsonResponseError` / `JsonResponseWithError`. Use `transport.get/post/patch/put/delete` for JSON or `request_raw` for binary responses.
- **`PaperlessCache`** (`cache.py`) — in-memory master data (e.g. `custom_fields`) shared between services via the runtime.
- **`PaperlessSettings`** (`settings.py`) — pydantic-settings model reading `PYPAPERLESS_URL` / `PYPAPERLESS_TOKEN` (prefix in `const.py: ENV_PREFIX`).

### Services and mixins

Resource services live in `pypaperless/services/`. They inherit `ResourceService` (which sets `_api_path` and `_resource`) and compose one or more mixins from `services/mixins/`:

| Mixin | Provides |
| --- | --- |
| `CallableService[T]` | `await service(pk)` returning a model instance |
| `IterableService[T]` | `async for item in service`, `pages()`, `as_list()`, `as_dict()`, and the `filter(**Unpack[XxxFilters])` async context manager (subclasses override `filter` with the typed TypedDict — always call `self._store_filters(**kwargs)`, never `super().filter()`) |
| `CreatableService[Draft]` | `service.create(**kwargs)` returns a draft; `await service.save(draft)` posts it. Requires `_draft_cls` |
| `UpdatableService[T]` | `await service.update(model, only_changed=True)` (PATCH) or `only_changed=False` (PUT), using the snapshot the model captured at load time |
| `DeletableService[T]` | `await service.delete(model, silent_fail=False)` |
| `SecurableService` | Adds `with_perms()` to request `?full_perms=true` and merges `permissions` payload on writes |

Reference implementations to copy when adding a new resource: `services/correspondents.py`, `services/tags.py`. For a document sub-service (`/api/documents/{id}/notes/`, `/history/`, `/versions/`, …) see the pattern in `services/documents/`.

### Models

All models inherit `PaperlessModel` (`models/base.py`):

- `_api_path: ClassVar[str]` is taken from `EndpointPath` in `const.py` and `{pk}`-formatted in `model_post_init`.
- `_snapshot` is captured on load so `UpdatableService` can diff changed fields. `refresh_from(data)` replaces fields in-place and rebuilds the snapshot.
- Drafts share a model file with their full counterpart (e.g. `Correspondent` and `CorrespondentDraft`). The draft's `validate_draft()` raises `DraftFieldRequiredError` for missing required fields; `serialize()` produces the POST payload.
- `PaperlessCustomDataModel` is the base for non-resource value objects (e.g. typed `CustomFieldValue` variants) — it carries opaque `_data` and overrides Pydantic's serializer.
- Public enum / filter / `TypedDict` types must be re-exported from `pypaperless/models/types.py`. Internal helpers stay prefixed with `_`.

### Dispatcher

`pypaperless/dispatch.py` is the bridge that powers `paperless.update(model)`, `paperless.delete(model)`, and `paperless.save(draft)` on the client. `DispatchableCachedProperty` (used in `client.py` instead of `functools.cached_property` for writable services) inspects the service's return annotation at class-definition time and registers `_resource_cls` / `_draft_cls` → `(attr_path,)` in a module-level map. `ModelDispatcher` walks that path on the live client and delegates to the appropriate mixin. **Consequences:**

- A service must use a real return-type annotation (`-> CorrespondentService`) on its `client.py` property — string / forward-reference annotations will silently skip registration.
- Use `dispatchable_cached_property` only on services that expose at least one of `CreatableService` / `UpdatableService` / `DeletableService`. Pure read-only services (e.g. `StatusService`, `StatisticService`) stay on plain `cached_property`.
- Sub-services that own their own writable models (e.g. `DocumentNoteService` exposed via `paperless.documents.notes`) are auto-registered too — the dispatcher scans the parent service's `@property` accessors for nested writable services.

### Filters

`pypaperless/models/filters.py` holds one `TypedDict` per filterable resource. Rules enforced by the `update-filters` skill:

- `total=False` everywhere; fields and classes sorted alphabetically.
- No field appears in more than one public TypedDict — shared fields go into a private `_XxxFilters` base (`_IdFilters`, `_NameFilters`, `_CreatedFilters`, `_ExpirationFilters`).
- `array[integer]` schema fields stay typed as `str` (comma-separated PK list — the iterable mixin handles `__in` lists by joining them automatically). `array[string+enum]` becomes `EnumType | str | list[EnumType | str]`.
- Re-export every public TypedDict from `models/types.py`.

### Builders

`pypaperless/builders/search.py` is the fluent `SearchQuery` (overloads `&` / `|` / `~` for Tantivy AND/OR/NOT) used by `SearchService`. `pypaperless/builders/custom_fields.py` builds the structured `custom_field_query` filter for documents. Both are reference docstring styles.

## Code conventions

- Ruff is configured with `select = ["ALL"]` (see `pyproject.toml`). The only project-wide ignores are the formatter-conflict ones (`COM812`, `ISC001`) plus a few opinionated rules (`ANN401`, `D203`, `D213`, `D417`, `PLR2004`, `PLR0913`, `RUF012`). Tests get `S101`/`SLF001`/`TC002`/`S105` extras via `tests/ruff.toml`.
- **No suppressions**: `# noqa`, `# type: ignore`, `# pragma: no cover` etc. are forbidden. Fix the root cause. The only allowed unscoped suppression is `# noqa: F401` on re-export lines inside `__init__.py`. If a fix genuinely cannot be done without one, ask before adding it.
- mypy runs in strict-ish mode against `pypaperless/` only (`tests/` is intentionally excluded). Untyped defs, implicit optional, and `Any`-returns are all errors.
- Pydantic v2 (`BaseModel`, `ConfigDict`, `model_validator`, `Field`, `PrivateAttr`). httpx for async HTTP. No sync HTTP, no `requests`.
- `@asynccontextmanager` is always wrapped in `try/finally` (see `IterableService._store_filters`).
- Max line length 100, target `py313`.

### Docstrings

Public symbols (anything not prefixed `_`): RST-style, one-line summary ending with a period, Google-style `Args:` block, and an `Example::` RST literal block. Sphinx cross-references for other library symbols (e.g. `:class:`~pypaperless.services.documents.DocumentService``). **Never** use Markdown fenced code blocks inside docstrings — they break the zensical doc build. Reference implementations: `pypaperless/builders/search.py`, `pypaperless/builders/custom_fields.py`, `pypaperless/client.py`.

Private / internal symbols (`_`-prefixed): one- or two-line docstring describing the _why_ only. No `Args:`, no example.

## Repository-specific skills

Two playbooks live under `.github/skills/`. Read them before touching the listed areas — they encode constraints discovered the hard way:

- **`.github/skills/add-resource/SKILL.md`** — full procedure for wiring up a new Paperless-ngx endpoint: `const.py` → model → service → `client.py` registration → fixture in `tests/data/` → unit tests → audit script → docs page + `zensical.toml` nav → smoketest. Includes a decision tree for paginated vs. flat-list vs. direct endpoints and the document sub-service pattern.
- **`.github/skills/update-filters/SKILL.md`** — procedure for syncing `models/filters.py` to upstream paperless-ngx FilterSets / `tests/data/schema.json`, including the schema-type → Python-type table and the inheritance / private-base rules.

## Documentation

User docs live under `docs/` and are built with [zensical](https://zensical.org) (config in `zensical.toml`). When adding a resource, add a `docs/resources/<name>.md` page, update the capability matrix in `docs/resources.md`, and add the nav entry to `zensical.toml` in alphabetical order. Concept docs (`docs/concepts/`) cover the document API, custom fields, custom field queries, permissions, and the search query builder.
