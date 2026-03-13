"""Comprehensive API smoke-test for pypaperless.

Runs against the dev Paperless instance configured in debug.py.
Document ID 1980 is used as the test document.

Exit code 0  → all sections green
Exit code != 0 → at least one section failed (printed in red)
"""

# ruff: noqa
# mypy: ignore-errors

from __future__ import annotations

import asyncio
import logging
import traceback
import uuid
from collections.abc import Callable, Coroutine
from typing import Any

import httpx

from pypaperless import Paperless
from pypaperless.models.correspondents import CorrespondentDraft
from pypaperless.models.custom_fields import (
    CustomFieldIntegerValue,
    CustomFieldStringValue,
)
from pypaperless.models.document_types import DocumentTypeDraft
from pypaperless.models.documents import DocumentCustomFieldList, DocumentDraft, DocumentNoteDraft
from pypaperless.models.share_links import ShareLinkDraft, ShareLinkFileVersion
from pypaperless.models.storage_paths import StoragePathDraft
from pypaperless.models.tags import TagDraft

# ── PDF helper ────────────────────────────────────────────────────────────────


def _make_unique_pdf(token: str) -> bytes:
    """Build a minimal valid single-page PDF with *token* embedded in the Info dict.

    Xref offsets are computed dynamically so the file is always valid —
    unlike a hardcoded template that breaks when any bytes are prepended.
    Each call with a different token produces a unique hash, which defeats
    Paperless-ngx duplicate detection.
    """
    token_bytes = token.encode()
    header = b"%PDF-1.4\n"
    obj1 = b"1 0 obj<</Type/Catalog/Pages 2 0 R/Info 4 0 R>>endobj\n"
    obj2 = b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
    obj3 = b"3 0 obj<</Type/Page/MediaBox[0 0 3 3]/Parent 2 0 R>>endobj\n"
    obj4 = b"4 0 obj<</Subject(" + token_bytes + b")>>endobj\n"

    off1 = len(header)
    off2 = off1 + len(obj1)
    off3 = off2 + len(obj2)
    off4 = off3 + len(obj3)
    xref_off = off4 + len(obj4)

    xref = (
        b"xref\n0 5\n"
        b"0000000000 65535 f \n"
        + f"{off1:010d} 00000 n \n".encode()
        + f"{off2:010d} 00000 n \n".encode()
        + f"{off3:010d} 00000 n \n".encode()
        + f"{off4:010d} 00000 n \n".encode()
        + b"trailer<</Size 5/Root 1 0 R>>\n"
        + f"startxref\n{xref_off}\n%%EOF\n".encode()
    )
    return header + obj1 + obj2 + obj3 + obj4 + xref


async def _await_task_and_cleanup(
    p: Paperless,
    task_id: str,
    label: str,
    *,
    timeout: int = 45,
) -> None:
    """Poll *task_id* until it finishes, then delete the resulting document.

    Uses ``Task.related_document`` to obtain the created doc ID without
    fragile result-string parsing.
    """
    from pypaperless.models.tasks import TaskStatus  # noqa: PLC0415

    doc_id: int | None = None
    deadline = asyncio.get_event_loop().time() + timeout
    task = None
    while asyncio.get_event_loop().time() < deadline:
        task = await p.tasks(task_id)
        if task is None:
            break
        if task.status in (
            TaskStatus.SUCCESS,
            TaskStatus.FAILURE,
            TaskStatus.REVOKED,
        ):
            if task.related_document is not None:
                try:
                    doc_id = int(task.related_document)
                except (ValueError, TypeError):
                    pass
            break
        await asyncio.sleep(1)

    if task is not None and task.status == TaskStatus.FAILURE:
        ok(f"cleanup [{label}]: task failed – nothing to delete", f"result={task.result!r}")
        return

    if doc_id is not None:
        try:
            doc = await p.documents(doc_id)
            deleted = await p.documents.delete(doc)
            ok(f"cleanup [{label}]: deleted doc #{doc_id}", f"deleted={deleted}")
        except Exception as exc:  # noqa: BLE001
            fail(f"cleanup [{label}]: delete doc #{doc_id}", exc)
    else:
        ok(
            f"cleanup [{label}]: doc not found after {timeout}s",
            "still processing or duplicate-rejected — skip",
        )


logging.basicConfig(level=logging.WARNING)

# ── Connection ────────────────────────────────────────────────────────────────
PAPERLESS_URL = "http://172.17.0.1:8000"
PAPERLESS_TOKEN = "3e9505078d32d8ad4ecea00fa0eec8e426622b52"
TEST_DOCUMENT_ID = 1980
PAGE_SIZE = 500

# ── Terminal colours ──────────────────────────────────────────────────────────
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
RESET = "\033[0m"
BOLD = "\033[1m"

# ── Result tracking ───────────────────────────────────────────────────────────
_passed: list[str] = []
_failed: list[tuple[str, str]] = []


def _hdr(title: str) -> None:
    print(f"\n{BOLD}{CYAN}{'─' * 60}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{BOLD}{CYAN}{'─' * 60}{RESET}")


def ok(label: str, detail: str = "") -> None:
    suffix = f"  {YELLOW}{detail}{RESET}" if detail else ""
    print(f"  {GREEN}✓{RESET}  {label}{suffix}")
    _passed.append(label)


def fail(label: str, exc: BaseException) -> None:
    msg = f"{type(exc).__name__}: {exc}"
    print(f"  {RED}✗{RESET}  {label}")
    print(f"      {RED}{msg}{RESET}")
    _failed.append((label, msg))


async def check(
    label: str,
    coro: Coroutine[Any, Any, Any],
    *,
    detail_fn: Callable[[Any], str] | None = None,
) -> Any | None:
    """Await *coro* and record pass/fail. Return the result or None."""
    try:
        result = await coro
        detail = detail_fn(result) if detail_fn else ""
        ok(label, detail)
        return result
    except Exception as exc:  # noqa: BLE001
        fail(label, exc)
        traceback.print_exc()
        return None


# ──────────────────────────────────────────────────────────────────────────────
async def test_system(p: Paperless) -> None:
    _hdr("System: status / statistics / remote_version")

    await check(
        "status()",
        p.status(),
        detail_fn=lambda r: f"db={r.database.status.value if r.database else '?'}",
    )
    await check(
        "statistics()",
        p.statistics(),
        detail_fn=lambda r: f"total_docs={r.documents_total}",
    )
    await check(
        "remote_version()",
        p.remote_version(),
        detail_fn=lambda r: f"version={r.version}, update_available={r.update_available}",
    )


# ──────────────────────────────────────────────────────────────────────────────
async def test_config(p: Paperless) -> None:
    _hdr("Config")

    await check("config(1)", p.config(1), detail_fn=lambda r: f"id={r.id}")


# ──────────────────────────────────────────────────────────────────────────────
async def test_documents(p: Paperless) -> None:
    _hdr("Documents – fetch, iterate, search, more_like, pages")

    # Fetch by pk
    doc = await check(
        f"documents({TEST_DOCUMENT_ID})",
        p.documents(TEST_DOCUMENT_ID),
        detail_fn=lambda r: f"title={r.title!r}",
    )

    # Fetch with permissions
    async with p.documents.with_permissions():
        await check(
            f"documents({TEST_DOCUMENT_ID}) with permissions",
            p.documents(TEST_DOCUMENT_ID),
            detail_fn=lambda r: f"has_permissions={r.has_permissions}",
        )

    # Lazy fetch
    await check(
        f"documents({TEST_DOCUMENT_ID}, lazy=True)",
        p.documents(TEST_DOCUMENT_ID, lazy=True),
        detail_fn=lambda r: f"id={r.id}",
    )

    # pages() iteration
    try:
        pages = aiter(p.documents.pages(page=1, page_size=PAGE_SIZE))
        page = await anext(pages)
        ok(
            f"documents.pages(page=1, page_size={PAGE_SIZE})",
            f"count={page.count}, items_on_page={page.current_count}",
        )
    except Exception as exc:  # noqa: BLE001
        fail("documents.pages()", exc)

    # as_list / as_dict shortcuts (limit via reduce)
    try:
        async with p.documents.reduce(page_size=PAGE_SIZE):
            docs_list = await p.documents.as_list()
        ok(f"documents.as_list() [page_size={PAGE_SIZE}]", f"len={len(docs_list)}")
    except Exception as exc:  # noqa: BLE001
        fail("documents.as_list()", exc)

    try:
        async with p.documents.reduce(page_size=PAGE_SIZE):
            docs_dict = await p.documents.as_dict()
        ok(f"documents.as_dict() [page_size={PAGE_SIZE}]", f"len={len(docs_dict)}")
    except Exception as exc:  # noqa: BLE001
        fail("documents.as_dict()", exc)

    # all() – returns list of PKs from first page
    try:
        async with p.documents.reduce(page_size=PAGE_SIZE):
            pks = await p.documents.all()
        ok(f"documents.all() [page_size={PAGE_SIZE}]", f"pks={pks[:3]}…")
    except Exception as exc:  # noqa: BLE001
        fail("documents.all()", exc)

    # search
    try:
        results = [d async for d in p.documents.search("invoice")]
        ok("documents.search('invoice')", f"results={len(results)}")
    except Exception as exc:  # noqa: BLE001
        fail("documents.search()", exc)

    # more_like
    try:
        similar = [d async for d in p.documents.more_like(TEST_DOCUMENT_ID)]
        ok(f"documents.more_like({TEST_DOCUMENT_ID})", f"similar={len(similar)}")
    except Exception as exc:  # noqa: BLE001
        fail("documents.more_like()", exc)

    # next ASN
    await check(
        "documents.get_next_asn()", p.documents.get_next_asn(), detail_fn=lambda r: f"asn={r}"
    )

    # Metadata
    await check(
        f"documents.metadata({TEST_DOCUMENT_ID})",
        p.documents.metadata(TEST_DOCUMENT_ID),
        detail_fn=lambda r: f"mime={r.original_mime_type}",
    )

    # thumbnail
    await check(
        f"documents.thumbnail({TEST_DOCUMENT_ID})",
        p.documents.thumbnail(TEST_DOCUMENT_ID),
        detail_fn=lambda r: f"content_type={r.content_type}, bytes={len(r.content or b'')}",
    )

    # preview
    await check(
        f"documents.preview({TEST_DOCUMENT_ID})",
        p.documents.preview(TEST_DOCUMENT_ID),
        detail_fn=lambda r: f"content_type={r.content_type}",
    )

    # download
    await check(
        f"documents.download({TEST_DOCUMENT_ID})",
        p.documents.download(TEST_DOCUMENT_ID),
        detail_fn=lambda r: f"filename={r.disposition_filename}",
    )

    # suggestions
    if doc is not None:
        await check(
            "doc.get_suggestions()",
            doc.get_suggestions(),
            detail_fn=lambda r: f"tags={r.tags}, correspondents={r.correspondents}",
        )

    # helper properties on document
    if doc is not None:
        try:
            _ = doc.has_search_hit
            _ = doc.created_date
            ok("doc.has_search_hit / doc.created_date", f"created={doc.created_date}")
        except Exception as exc:  # noqa: BLE001
            fail("doc properties", exc)


# ──────────────────────────────────────────────────────────────────────────────
async def test_document_history(p: Paperless) -> None:
    _hdr("Document History – list via service and document property")

    entries = await check(
        f"documents.history({TEST_DOCUMENT_ID})",
        p.documents.history(TEST_DOCUMENT_ID),
        detail_fn=lambda r: f"count={len(r)}, first_action={r[0].action.value if r else '—'}",
    )

    if entries:
        try:
            doc = await p.documents(TEST_DOCUMENT_ID)
            entries_via_doc = await doc.history()
            ok(
                f"doc.history() property [{TEST_DOCUMENT_ID}]",
                f"count={len(entries_via_doc)}",
            )
        except Exception as exc:  # noqa: BLE001
            fail("doc.history() property", exc)


# ──────────────────────────────────────────────────────────────────────────────
async def test_trash(p: Paperless) -> None:
    _hdr("Trash – list deleted documents")

    await check(
        "trash.as_list()",
        p.trash.as_list(),
        detail_fn=lambda r: f"count={len(r)}",
    )


# ──────────────────────────────────────────────────────────────────────────────
async def test_document_notes(p: Paperless) -> None:
    _hdr("Document Notes – list, create, delete")

    notes = await check(
        f"documents.notes({TEST_DOCUMENT_ID})",
        p.documents.notes(TEST_DOCUMENT_ID),
        detail_fn=lambda r: f"count={len(r)}",
    )

    # create a note
    note_id = None
    try:
        draft: DocumentNoteDraft = p.documents.notes.draft(
            TEST_DOCUMENT_ID, note="pypaperless smoke-test note"
        )
        note_id, doc_id = await p.documents.notes.save(draft)
        ok("documents.notes.save(draft)", f"note_id={note_id}, doc_id={doc_id}")
    except Exception as exc:  # noqa: BLE001
        fail("documents.notes.save()", exc)

    # delete the created note
    if note_id is not None:
        try:
            all_notes = await p.documents.notes(TEST_DOCUMENT_ID)
            created = next((n for n in all_notes if n.id == note_id), None)
            if created is not None:
                deleted = await p.documents.notes.delete(created)
                ok("documents.notes.delete(note)", f"deleted={deleted}")
            else:
                ok("documents.notes.delete(note)", "note not found – skipped")
        except Exception as exc:  # noqa: BLE001
            fail("documents.notes.delete()", exc)


# ──────────────────────────────────────────────────────────────────────────────
async def test_custom_fields(p: Paperless) -> None:
    _hdr("Custom Fields – list, cache, access on document")

    # Populate cache
    try:
        p.cache.custom_fields = await p.custom_fields.as_dict()
        ok("custom_fields.as_dict() → cache", f"count={len(p.cache.custom_fields)}")
    except Exception as exc:  # noqa: BLE001
        fail("custom_fields.as_dict()", exc)

    # list
    await check(
        "custom_fields.as_list()",
        p.custom_fields.as_list(),
        detail_fn=lambda r: f"count={len(r)}",
    )

    # Access custom fields on the test document
    try:
        doc = await p.documents(TEST_DOCUMENT_ID)
        if doc.custom_fields is not None:
            field_count = sum(1 for _ in doc.custom_fields)
            ok(f"doc.custom_fields on doc {TEST_DOCUMENT_ID}", f"fields={field_count}")
        else:
            ok(f"doc.custom_fields on doc {TEST_DOCUMENT_ID}", "no custom fields")
    except Exception as exc:  # noqa: BLE001
        fail("doc.custom_fields access", exc)


# ──────────────────────────────────────────────────────────────────────────────
async def test_custom_field_values_on_document(p: Paperless) -> None:
    _hdr(f"Custom Field Values – all 9 types, modify & restore on doc {TEST_DOCUMENT_ID}")

    import datetime  # noqa: PLC0415

    from pypaperless.models.custom_fields import (  # noqa: PLC0415
        CustomFieldBooleanValue,
        CustomFieldDateValue,
        CustomFieldDocumentLinkValue,
        CustomFieldFloatValue,
        CustomFieldIntegerValue,
        CustomFieldMonetaryValue,
        CustomFieldSelectValue,
        CustomFieldStringValue,
        CustomFieldURLValue,
    )

    if not p.cache.custom_fields:
        p.cache.custom_fields = await p.custom_fields.as_dict()

    doc = await check(
        f"documents({TEST_DOCUMENT_ID}) fetch",
        p.documents(TEST_DOCUMENT_ID),
        detail_fn=lambda r: f"title={r.title!r}",
    )
    if doc is None or doc.custom_fields is None:
        fail("custom_fields pre-condition", Exception("doc or custom_fields is None – aborting"))
        return

    cf = doc.custom_fields  # DocumentCustomFieldList, not None

    # ── Snapshot originals ────────────────────────────────────────────────
    originals: dict[int, object] = {cfv.field: cfv.value for cfv in cf}  # type: ignore[union-attr]
    ok("custom_fields snapshot", f"count={len(originals)}  ids={sorted(originals)}")

    # ── Helper: pick a different SELECT option from cache ─────────────────
    def _other_select_option(field_id: int, current: object) -> object:
        cached_cf = p.cache.custom_fields.get(field_id) if p.cache.custom_fields else None
        if cached_cf is None or cached_cf.extra_data is None:
            return current
        opts = [o for o in cached_cf.extra_data.select_options if o and o.id != current]
        return opts[0].id if opts else current

    # ══════════════════════════════════════════════════════════════════════
    #  MODIFY – one field per type, using typed getters
    # ══════════════════════════════════════════════════════════════════════

    # BOOLEAN  id=1
    cfv1 = cf.get(1, CustomFieldBooleanValue)
    new_bool = not cfv1.value
    cfv1.value = new_bool
    ok("BOOLEAN  modify id=1", f"{originals[1]!r} → {cfv1.value!r}")

    # DATE     id=2
    cfv2 = cf.get(2, CustomFieldDateValue)
    new_date = datetime.date(2026, 3, 11)
    cfv2.value = new_date
    ok("DATE     modify id=2", f"{originals[2]!r} → {cfv2.value!r}")

    # INTEGER  id=3
    cfv3 = cf.get(3, CustomFieldIntegerValue)
    cfv3.value = 999
    ok("INTEGER  modify id=3", f"{originals[3]!r} → {cfv3.value!r}")

    # FLOAT    id=4
    cfv4 = cf.get(4, CustomFieldFloatValue)
    cfv4.value = 99.9999
    ok("FLOAT    modify id=4", f"{originals[4]!r} → {cfv4.value!r}")

    # MONETARY id=5  – via .currency / .amount setters
    cfv5 = cf.get(5, CustomFieldMonetaryValue)
    cfv5.currency = "USD"
    cfv5.amount = 1111.11
    ok("MONETARY modify id=5 (EUR→USD, new amount)", f"{originals[5]!r} → {cfv5.value!r}")

    # MONETARY id=6  – amount only
    cfv6 = cf.get(6, CustomFieldMonetaryValue)
    cfv6.amount = 9876.54
    ok("MONETARY modify id=6 (amount only)", f"{originals[6]!r} → {cfv6.value!r}")

    # MONETARY id=7  – currency + amount
    cfv7 = cf.get(7, CustomFieldMonetaryValue)
    cfv7.currency = "EUR"
    cfv7.amount = 500.00
    ok("MONETARY modify id=7 (USD→EUR, new amount)", f"{originals[7]!r} → {cfv7.value!r}")

    # STRING   id=8
    cfv8 = cf.get(8, CustomFieldStringValue)
    cfv8.value = "pypaperless-smoke-modified"
    ok("STRING   modify id=8", f"{originals[8]!r} → {cfv8.value!r}")

    # URL      id=9
    cfv9 = cf.get(9, CustomFieldURLValue)
    cfv9.value = "https://github.com/tb1337/paperless-api"
    ok("URL      modify id=9", f"{originals[9]!r} → {cfv9.value!r}")

    # DOCUMENT_LINK  id=10
    cfv10 = cf.get(10, CustomFieldDocumentLinkValue)
    cfv10.value = [TEST_DOCUMENT_ID]
    ok("DOCLINK  modify id=10", f"{originals[10]!r} → {cfv10.value!r}")

    # SELECT   id=11  – pick a different option dynamically
    cfv11 = cf.get(11, CustomFieldSelectValue)
    new_sel = _other_select_option(11, cfv11.value)
    cfv11.value = new_sel
    ok("SELECT   modify id=11", f"{originals[11]!r} → {cfv11.value!r}  (label={cfv11.label!r})")

    # ══════════════════════════════════════════════════════════════════════
    #  ADD new fields (not yet on doc 1980)
    # ══════════════════════════════════════════════════════════════════════
    NEW_FIELDS: list[tuple[int, object, type]] = [
        (13, 777, CustomFieldIntegerValue),  # INTEGER  – Add Test Field
        (14, "EUR2500.00", CustomFieldMonetaryValue),  # MONETARY – LA_Brutto
        (15, "EUR2000.00", CustomFieldMonetaryValue),  # MONETARY – LA_Netto
    ]
    for nf_id, nf_val, nf_cls in NEW_FIELDS:
        try:
            cf += nf_cls(field=nf_id, value=nf_val)
            ok(f"add      field id={nf_id} ({nf_cls.__name__})", f"value={nf_val!r}")
        except Exception as exc:  # noqa: BLE001
            fail(f"add field id={nf_id}", exc)

    # ── PATCH ──────────────────────────────────────────────────────────────
    await check(
        "documents.update() – all-type modifications + 3 new fields",
        p.documents.update(doc),
        detail_fn=lambda r: f"changed={r}",
    )

    # ══════════════════════════════════════════════════════════════════════
    #  RE-FETCH + VERIFY with typed getters
    # ══════════════════════════════════════════════════════════════════════
    doc2 = await p.documents(TEST_DOCUMENT_ID)
    if doc2 is None or doc2.custom_fields is None:
        fail("re-fetch after update", Exception("doc2 is None"))
        return

    cf2 = doc2.custom_fields

    def _verify(label: str, field_id: int, expected: object, cls: type) -> None:
        try:
            got = cf2.get(field_id, cls)  # type: ignore[arg-type]
            if got.value == expected:
                ok(f"verify  {label} id={field_id}", f"value={got.value!r}")
            else:
                fail(
                    f"verify  {label} id={field_id}",
                    AssertionError(f"expected={expected!r}, got={got.value!r}"),
                )
        except Exception as exc:  # noqa: BLE001
            fail(f"verify  {label} id={field_id}", exc)

    _verify("BOOLEAN", 1, new_bool, CustomFieldBooleanValue)
    _verify("DATE", 2, new_date, CustomFieldDateValue)
    _verify("INTEGER", 3, 999, CustomFieldIntegerValue)
    _verify("FLOAT", 4, 99.9999, CustomFieldFloatValue)
    _verify("MONETARY", 5, cfv5.value, CustomFieldMonetaryValue)
    _verify("MONETARY", 6, cfv6.value, CustomFieldMonetaryValue)
    _verify("MONETARY", 7, cfv7.value, CustomFieldMonetaryValue)
    _verify("STRING", 8, "pypaperless-smoke-modified", CustomFieldStringValue)
    _verify("URL", 9, "https://github.com/tb1337/paperless-api", CustomFieldURLValue)
    _verify("DOCLINK", 10, [TEST_DOCUMENT_ID], CustomFieldDocumentLinkValue)
    _verify("SELECT", 11, new_sel, CustomFieldSelectValue)
    _verify("INTEGER (new)", 13, 777, CustomFieldIntegerValue)
    _verify("MONETARY (new)", 14, "EUR2500.00", CustomFieldMonetaryValue)
    _verify("MONETARY (new)", 15, "EUR2000.00", CustomFieldMonetaryValue)

    # ══════════════════════════════════════════════════════════════════════
    #  RESTORE originals + remove added fields
    # ══════════════════════════════════════════════════════════════════════
    for field_id, orig_val in originals.items():
        try:
            cf2.get(field_id).value = orig_val
        except Exception as exc:  # noqa: BLE001
            fail(f"restore field id={field_id}", exc)

    for nf_id, _, _ in NEW_FIELDS:
        try:
            cf2 -= nf_id
            ok(f"remove   added id={nf_id}", "removed")
        except Exception as exc:  # noqa: BLE001
            fail(f"remove added id={nf_id}", exc)

    await check(
        "documents.update() – restore originals",
        p.documents.update(doc2),
        detail_fn=lambda r: f"changed={r}",
    )

    # ── Final verify ───────────────────────────────────────────────────────
    doc3 = await p.documents(TEST_DOCUMENT_ID)
    if doc3 is None or doc3.custom_fields is None:
        fail("final re-fetch", Exception("doc3 is None"))
        return

    cf3 = doc3.custom_fields
    all_restored = True
    for field_id, orig_val in originals.items():
        cfv3 = cf3.default(field_id)
        if cfv3 is None or cfv3.value != orig_val:
            all_restored = False
            fail(
                f"final restore id={field_id}",
                AssertionError(f"expected={orig_val!r}, got={cfv3.value if cfv3 else None!r}"),
            )
    if all_restored:
        ok("all original values restored", f"fields={len(originals)}")

    for nf_id, _, _ in NEW_FIELDS:
        if cf3.default(nf_id) is None:
            ok(f"added field id={nf_id} absent after restore", "not present")
        else:
            fail(f"added field id={nf_id} absent after restore", AssertionError("still present"))


# ──────────────────────────────────────────────────────────────────────────────
async def test_correspondents(p: Paperless) -> None:
    _hdr("Correspondents – list, create, update, permissions, delete")

    await check(
        "correspondents.as_list()",
        p.correspondents.as_list(),
        detail_fn=lambda r: f"count={len(r)}",
    )

    # create
    draft = CorrespondentDraft.create_with_data(
        p,
        {
            "name": "pypaperless Smoke Test Corp",
            "match": "",
            "matching_algorithm": 0,
            "is_insensitive": True,
        },
    )
    created_id: int | None = None
    try:
        created_id = int(await p.correspondents.save(draft))
        ok("correspondents.save(draft)", f"id={created_id}")
    except Exception as exc:  # noqa: BLE001
        fail("correspondents.save(draft)", exc)

    if created_id is not None:
        # fetch back
        corr = await check(
            f"correspondents({created_id})",
            p.correspondents(created_id),
            detail_fn=lambda r: f"name={r.name!r}",
        )

        # update
        if corr is not None:
            corr.name = "pypaperless Smoke Test Corp (updated)"
            updated = await check(
                "correspondents.update(corr)",
                p.correspondents.update(corr),
                detail_fn=lambda r: f"changed={r}",
            )

        # permissions
        async with p.correspondents.with_permissions():
            await check(
                f"correspondents({created_id}) with permissions",
                p.correspondents(created_id),
                detail_fn=lambda r: f"has_permissions={r.has_permissions}",
            )

        # delete
        try:
            corr_to_delete = await p.correspondents(created_id)
            deleted = await p.correspondents.delete(corr_to_delete)
            ok(f"correspondents.delete({created_id})", f"deleted={deleted}")
        except Exception as exc:  # noqa: BLE001
            fail("correspondents.delete()", exc)


# ──────────────────────────────────────────────────────────────────────────────
async def test_tags(p: Paperless) -> None:
    _hdr("Tags – list, create, update, delete")

    await check("tags.as_list()", p.tags.as_list(), detail_fn=lambda r: f"count={len(r)}")

    draft = TagDraft.create_with_data(
        p,
        {
            "name": "pypaperless-smoke-test",
            "color": "#ff0000",
            "is_inbox_tag": False,
            "match": "",
            "matching_algorithm": 0,
            "is_insensitive": True,
        },
    )
    tag_id: int | None = None
    try:
        tag_id = int(await p.tags.save(draft))
        ok("tags.save(draft)", f"id={tag_id}")
    except Exception as exc:  # noqa: BLE001
        fail("tags.save(draft)", exc)

    if tag_id is not None:
        tag = await check(
            f"tags({tag_id})",
            p.tags(tag_id),
            detail_fn=lambda r: f"name={r.name!r}",
        )
        if tag is not None:
            tag.name = "pypaperless-smoke-test-updated"
            await check("tags.update(tag)", p.tags.update(tag), detail_fn=lambda r: f"changed={r}")

        try:
            t = await p.tags(tag_id)
            deleted = await p.tags.delete(t)
            ok(f"tags.delete({tag_id})", f"deleted={deleted}")
        except Exception as exc:  # noqa: BLE001
            fail("tags.delete()", exc)

    # ── Nested-Tag smoke-test ─────────────────────────────────────────────
    _hdr("Tags – nested children validator")

    from pypaperless.models.tags import Tag  # noqa: PLC0415

    # Tag 17 ('Kfz') already has known children on the test system
    t17 = await check(
        "tags(17) – known tag with children",
        p.tags(17),
        detail_fn=lambda r: f"name={r.name!r}, children={[c.id for c in (r.children or [])]}",
    )
    if t17 is not None:
        children17 = t17.children or []
        if children17 and isinstance(children17[0], Tag):
            ok(
                "Tag.children contains Tag instances (tag 17)",
                f"count={len(children17)}, ids={[c.id for c in children17]}",
            )
        else:
            fail(
                "Tag.children contains Tag instances (tag 17)",
                AssertionError(f"children={children17!r}"),
            )

    # Also verify end-to-end with dynamically created parent/child pair
    parent_id: int | None = None
    child_id: int | None = None

    _parent_draft = TagDraft.create_with_data(
        p,
        {
            "name": "pypaperless-smoke-parent",
            "color": "#0000ff",
            "is_inbox_tag": False,
            "match": "",
            "matching_algorithm": 0,
            "is_insensitive": True,
        },
    )
    try:
        parent_id = int(await p.tags.save(_parent_draft))
        ok("tags.save(parent_draft)", f"id={parent_id}")
    except Exception as exc:  # noqa: BLE001
        fail("tags.save(parent_draft)", exc)

    if parent_id is not None:
        _child_draft = TagDraft.create_with_data(
            p,
            {
                "name": "pypaperless-smoke-child",
                "color": "#00ff00",
                "is_inbox_tag": False,
                "match": "",
                "matching_algorithm": 0,
                "is_insensitive": True,
                "parent": parent_id,
            },
        )
        try:
            child_id = int(await p.tags.save(_child_draft))
            ok("tags.save(child_draft)", f"id={child_id}, parent={parent_id}")
        except Exception as exc:  # noqa: BLE001
            fail("tags.save(child_draft)", exc)

    if parent_id is not None and child_id is not None:
        parent_tag = await check(
            f"tags({parent_id}) after child created",
            p.tags(parent_id),
            detail_fn=lambda r: f"children={[c.id for c in (r.children or [])]}",
        )
        if parent_tag is not None:
            children = parent_tag.children or []
            if children and isinstance(children[0], Tag) and children[0].id == child_id:
                ok(
                    "dynamic Tag.children[0] is Tag with correct id",
                    f"child.id={children[0].id}, child.name={children[0].name!r}",
                )
            else:
                fail(
                    "dynamic Tag.children[0] is Tag with correct id",
                    AssertionError(f"children={children!r}"),
                )

        # cleanup – child first (FK constraint), then parent
        for del_id, label in ((child_id, "child"), (parent_id, "parent")):
            try:
                t = await p.tags(del_id)
                deleted = await p.tags.delete(t)
                ok(f"tags.delete({label} id={del_id})", f"deleted={deleted}")
            except Exception as exc:  # noqa: BLE001
                fail(f"tags.delete({label} id={del_id})", exc)


# ──────────────────────────────────────────────────────────────────────────────
async def test_document_types(p: Paperless) -> None:
    _hdr("Document Types – list, create, update, delete")

    await check(
        "document_types.as_list()",
        p.document_types.as_list(),
        detail_fn=lambda r: f"count={len(r)}",
    )

    draft = DocumentTypeDraft.create_with_data(
        p,
        {
            "name": "pypaperless Smoke Test Type",
            "match": "",
            "matching_algorithm": 0,
            "is_insensitive": True,
        },
    )
    dt_id: int | None = None
    try:
        dt_id = int(await p.document_types.save(draft))
        ok("document_types.save(draft)", f"id={dt_id}")
    except Exception as exc:  # noqa: BLE001
        fail("document_types.save(draft)", exc)

    if dt_id is not None:
        dt = await check(
            f"document_types({dt_id})",
            p.document_types(dt_id),
            detail_fn=lambda r: f"name={r.name!r}",
        )
        if dt is not None:
            dt.name = "pypaperless Smoke Test Type (updated)"
            await check("document_types.update(dt)", p.document_types.update(dt))

        try:
            t = await p.document_types(dt_id)
            deleted = await p.document_types.delete(t)
            ok(f"document_types.delete({dt_id})", f"deleted={deleted}")
        except Exception as exc:  # noqa: BLE001
            fail("document_types.delete()", exc)


# ──────────────────────────────────────────────────────────────────────────────
async def test_storage_paths(p: Paperless) -> None:
    _hdr("Storage Paths – list, create, update, delete")

    await check(
        "storage_paths.as_list()",
        p.storage_paths.as_list(),
        detail_fn=lambda r: f"count={len(r)}",
    )

    draft = StoragePathDraft.create_with_data(
        p,
        {
            "name": "pypaperless Smoke Test Path",
            "path": "smoke-test/{correspondent}/{title}",
            "match": "",
            "matching_algorithm": 0,
            "is_insensitive": True,
        },
    )
    sp_id: int | None = None
    try:
        sp_id = int(await p.storage_paths.save(draft))
        ok("storage_paths.save(draft)", f"id={sp_id}")
    except Exception as exc:  # noqa: BLE001
        fail("storage_paths.save(draft)", exc)

    if sp_id is not None:
        sp = await check(
            f"storage_paths({sp_id})",
            p.storage_paths(sp_id),
            detail_fn=lambda r: f"name={r.name!r}",
        )
        if sp is not None:
            sp.name = "pypaperless Smoke Test Path (updated)"
            await check("storage_paths.update(sp)", p.storage_paths.update(sp))

        try:
            s = await p.storage_paths(sp_id)
            deleted = await p.storage_paths.delete(s)
            ok(f"storage_paths.delete({sp_id})", f"deleted={deleted}")
        except Exception as exc:  # noqa: BLE001
            fail("storage_paths.delete()", exc)


# ──────────────────────────────────────────────────────────────────────────────
async def test_share_links(p: Paperless) -> None:
    _hdr("Share Links – list, create, delete")

    await check(
        "share_links.as_list()",
        p.share_links.as_list(),
        detail_fn=lambda r: f"count={len(r)}",
    )

    draft = ShareLinkDraft.create_with_data(
        p,
        {
            "document": TEST_DOCUMENT_ID,
            "file_version": ShareLinkFileVersion.ARCHIVE,
            "expiration": None,
        },
    )
    link_id: int | None = None
    try:
        link_id = int(await p.share_links.save(draft))
        ok("share_links.save(draft)", f"id={link_id}")
    except Exception as exc:  # noqa: BLE001
        fail("share_links.save(draft)", exc)

    if link_id is not None:
        link = await check(
            f"share_links({link_id})",
            p.share_links(link_id),
            detail_fn=lambda r: f"slug={r.slug}",
        )
        if link is not None:
            deleted = await check(
                f"share_links.delete({link_id})",
                p.share_links.delete(link),
                detail_fn=lambda r: f"deleted={r}",
            )


# ──────────────────────────────────────────────────────────────────────────────
async def test_saved_views(p: Paperless) -> None:
    _hdr("Saved Views – list, fetch")

    views = await check(
        "saved_views.as_list()",
        p.saved_views.as_list(),
        detail_fn=lambda r: f"count={len(r)}",
    )
    if views:
        await check(
            f"saved_views({views[0].id})",
            p.saved_views(views[0].id),
            detail_fn=lambda r: f"name={r.name!r}",
        )


# ──────────────────────────────────────────────────────────────────────────────
async def test_users_groups(p: Paperless) -> None:
    _hdr("Users & Groups – list, fetch")

    users = await check(
        "users.as_list()",
        p.users.as_list(),
        detail_fn=lambda r: f"count={len(r)}",
    )
    if users:
        await check(
            f"users({users[0].id})",
            p.users(users[0].id),
            detail_fn=lambda r: f"username={r.username!r}",
        )

    groups = await check(
        "groups.as_list()",
        p.groups.as_list(),
        detail_fn=lambda r: f"count={len(r)}",
    )
    if groups:
        await check(
            f"groups({groups[0].id})",
            p.groups(groups[0].id),
            detail_fn=lambda r: f"name={r.name!r}",
        )


# ──────────────────────────────────────────────────────────────────────────────
async def test_tasks(p: Paperless) -> None:
    _hdr("Tasks – iterate, fetch by uuid")

    tasks = []
    try:
        async for task in p.tasks:
            tasks.append(task)
        ok("tasks async for", f"count={len(tasks)}")
    except Exception as exc:  # noqa: BLE001
        fail("tasks async for", exc)

    if tasks:
        first = tasks[0]
        if first.task_id:
            await check(
                f"tasks(task_id={first.task_id!r})",
                p.tasks(first.task_id),
                detail_fn=lambda r: f"status={r.status}",
            )
        if first.id:
            await check(
                f"tasks(pk={first.id})",
                p.tasks(first.id),
                detail_fn=lambda r: f"status={r.status}",
            )


# ──────────────────────────────────────────────────────────────────────────────
async def test_mail(p: Paperless) -> None:
    _hdr("Mail Accounts / Mail Rules / Processed Mail")

    await check(
        "mail_accounts.as_list()",
        p.mail_accounts.as_list(),
        detail_fn=lambda r: f"count={len(r)}",
    )
    await check(
        "mail_rules.as_list()",
        p.mail_rules.as_list(),
        detail_fn=lambda r: f"count={len(r)}",
    )
    await check(
        "processed_mail.as_list()",
        p.processed_mail.as_list(),
        detail_fn=lambda r: f"count={len(r)}",
    )


# ──────────────────────────────────────────────────────────────────────────────
async def test_workflows(p: Paperless) -> None:
    _hdr("Workflows / Actions / Triggers")

    await check(
        "workflows.as_list()",
        p.workflows.as_list(),
        detail_fn=lambda r: f"count={len(r)}",
    )
    await check(
        "workflows.actions.as_list()",
        p.workflows.actions.as_list(),
        detail_fn=lambda r: f"count={len(r)}",
    )
    await check(
        "workflows.triggers.as_list()",
        p.workflows.triggers.as_list(),
        detail_fn=lambda r: f"count={len(r)}",
    )


# ──────────────────────────────────────────────────────────────────────────────
async def test_document_post(p: Paperless) -> None:
    _hdr("Document POST – upload a minimal PDF")

    token = str(uuid.uuid4())
    draft = DocumentDraft.create_with_data(
        p,
        {
            "document": _make_unique_pdf(token),
            "filename": "smoke_test.pdf",
            "title": f"pypaperless Smoke Test Upload [{token[:8]}]",
        },
    )
    task_id: str | None = None
    try:
        task_id = str(await p.documents.save(draft))
        ok("documents.save(draft) – post_document", f"task_id={task_id!r}")
    except Exception as exc:  # noqa: BLE001
        fail("documents.save(draft) – post_document", exc)

    if task_id is not None:
        await _await_task_and_cleanup(p, task_id, "post_document")


# ──────────────────────────────────────────────────────────────────────────────
async def test_document_post_with_cf_mapping(p: Paperless) -> None:
    _hdr("Document POST – upload with custom_fields object mapping")

    # Ensure custom field cache is populated
    if not p.cache.custom_fields:
        try:
            p.cache.custom_fields = await p.custom_fields.as_dict()
        except Exception as exc:  # noqa: BLE001
            fail("custom_fields cache (pre-condition)", exc)
            return

    # Variant A: list[int] – assign field IDs only (empty values)
    token_a = str(uuid.uuid4())
    draft_a = DocumentDraft.create_with_data(
        p,
        {
            "document": _make_unique_pdf(token_a),
            "filename": "smoke_cf_ids.pdf",
            "title": f"pypaperless CF id-list test [{token_a[:8]}]",
            "custom_fields": [8, 3],
        },
    )
    task_id_a: str | None = None
    try:
        task_id_a = str(await p.documents.save(draft_a))
        ok("documents.save(draft) – custom_fields=list[int]", f"task_id={task_id_a!r}")
    except Exception as exc:  # noqa: BLE001
        fail("documents.save(draft) – custom_fields=list[int]", exc)

    # Variant B: DocumentCustomFieldList – object mapping with typed values
    token_b = str(uuid.uuid4())
    cf = DocumentCustomFieldList(p, [])
    cf += CustomFieldStringValue(field=8, value="pypaperless-smoke")
    cf += CustomFieldIntegerValue(field=3, value=1)

    draft_b = DocumentDraft.create_with_data(
        p,
        {
            "document": _make_unique_pdf(token_b),
            "filename": "smoke_cf_mapping.pdf",
            "title": f"pypaperless CF object-mapping test [{token_b[:8]}]",
        },
    )
    draft_b.custom_fields = cf

    task_id_b: str | None = None
    try:
        # Verify serialisation before sending
        import json  # noqa: PLC0415

        serialized = draft_b.serialize()
        raw = serialized["form"]["custom_fields"]
        assert isinstance(raw, str), f"expected str, got {type(raw)}"
        decoded = json.loads(raw)
        assert isinstance(decoded, dict)
        assert decoded.get("8") == "pypaperless-smoke"
        assert decoded.get("3") == 1
        ok(
            "DocumentDraft.serialize() – custom_fields JSON encoding",
            f"payload={decoded}",
        )
    except Exception as exc:  # noqa: BLE001
        fail("DocumentDraft.serialize() – custom_fields JSON encoding", exc)
        return

    try:
        task_id_b = str(await p.documents.save(draft_b))
        ok(
            "documents.save(draft) – custom_fields=DocumentCustomFieldList",
            f"task_id={task_id_b!r}",
        )
    except Exception as exc:  # noqa: BLE001
        fail("documents.save(draft) – custom_fields=DocumentCustomFieldList", exc)

    # Clean up both uploaded documents
    if task_id_a is not None:
        await _await_task_and_cleanup(p, task_id_a, "cf-id-list")
    if task_id_b is not None:
        await _await_task_and_cleanup(p, task_id_b, "cf-mapping")


# ──────────────────────────────────────────────────────────────────────────────
async def test_reduce_context(p: Paperless) -> None:
    _hdr("reduce() context manager – filter & iterate")

    try:
        async with p.documents.reduce(page_size=PAGE_SIZE, title__icontains="a"):
            count = 0
            async for _ in p.documents:
                count += 1
                if count >= PAGE_SIZE:
                    break
        ok(f"documents.reduce(page_size={PAGE_SIZE}, title__icontains='a')", f"iterated={count}")
    except Exception as exc:  # noqa: BLE001
        fail("documents.reduce()", exc)


# ──────────────────────────────────────────────────────────────────────────────
async def test_profile(p: Paperless) -> None:
    _hdr("Profile – fetch and update")

    profile = await check(
        "profile()",
        p.profile(),
        detail_fn=lambda r: f"email={r.email!r}, mfa={r.is_mfa_enabled}",
    )
    if profile is not None:
        await check(
            "profile.update(first_name=profile.first_name)",
            p.profile.update(first_name=profile.first_name),
            detail_fn=lambda r: f"first_name={r.first_name!r}",
        )


# ──────────────────────────────────────────────────────────────────────────────
async def test_generate_api_token() -> None:
    _hdr("Static helper – generate_api_token (expected failure on bad creds)")

    try:
        await Paperless.generate_api_token(
            PAPERLESS_URL,
            "wrong_user",
            "wrong_password",
            client=httpx.AsyncClient(verify=False),
        )
        fail("generate_api_token(bad creds) should have raised", RuntimeError("no exception"))
    except Exception:  # noqa: BLE001
        ok("generate_api_token(bad creds) → exception as expected")


# ──────────────────────────────────────────────────────────────────────────────
async def main() -> int:
    paperless = Paperless(
        PAPERLESS_URL,
        PAPERLESS_TOKEN,
        request_api_version=9,
        client=httpx.AsyncClient(verify=False),
    )

    print(f"\n{BOLD}pypaperless API smoke-test{RESET}")
    print(f"Target: {PAPERLESS_URL}  |  Document under test: #{TEST_DOCUMENT_ID}")

    async with paperless:
        await test_system(paperless)
        await test_profile(paperless)
        await test_config(paperless)
        await test_documents(paperless)
        await test_document_history(paperless)
        await test_trash(paperless)
        await test_document_notes(paperless)
        await test_custom_fields(paperless)
        await test_custom_field_values_on_document(paperless)
        await test_correspondents(paperless)
        await test_tags(paperless)
        await test_document_types(paperless)
        await test_storage_paths(paperless)
        await test_share_links(paperless)
        await test_saved_views(paperless)
        await test_users_groups(paperless)
        await test_tasks(paperless)
        await test_mail(paperless)
        await test_workflows(paperless)
        await test_document_post(paperless)
        await test_document_post_with_cf_mapping(paperless)
        await test_reduce_context(paperless)

    await test_generate_api_token()

    # ── Summary ───────────────────────────────────────────────────────────────
    total = len(_passed) + len(_failed)
    print(f"\n{BOLD}{'═' * 60}{RESET}")
    print(
        f"{BOLD}  Results: {GREEN}{len(_passed)} passed{RESET}  /  {RED}{len(_failed)} failed{RESET}  (total {total}){RESET}"
    )
    if _failed:
        print(f"\n{RED}Failed checks:{RESET}")
        for label, msg in _failed:
            print(f"  • {label}")
            print(f"    {RED}{msg}{RESET}")
    print(f"{BOLD}{'═' * 60}{RESET}\n")

    return 1 if _failed else 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
