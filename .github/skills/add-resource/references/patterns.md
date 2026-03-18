# Code Patterns & Templates

## Model Templates

### Standard paginated resource model

```python
# pypaperless/models/widgets.py
import datetime
from enum import StrEnum
from typing import ClassVar

from pypaperless.const import API_PATH
from . import mixins
from .base import PaperlessModel


class WidgetColor(StrEnum):
    RED = "red"
    BLUE = "blue"


class Widget(PaperlessModel, mixins.SecurableMixin):
    """Represent a Paperless `Widget`."""

    _api_path: ClassVar[str] = API_PATH["widgets_single"]

    id: int | None = None
    name: str | None = None
    color: WidgetColor | None = None
    created: datetime.datetime | None = None
    owner: int | None = None
    user_can_change: bool | None = None


class WidgetDraft(PaperlessModel, mixins.CreatableMixin):
    """Represent a new `Widget` not yet stored in Paperless."""

    _api_path: ClassVar[str] = API_PATH["widgets"]
    _create_required_fields: ClassVar[set[str]] = {"name"}

    name: str | None = None
    color: WidgetColor | None = None
```

### Sub-resource model (document-attached, flat list)

```python
class DocumentHistory(PaperlessModel):
    """Represent a single Paperless document history (audit-log) entry."""

    _api_path: ClassVar[str] = API_PATH["documents_history"]

    id: int | None = None
    document: int | None = None        # injected by service
    timestamp: datetime.datetime | None = None
    action: DocumentHistoryAction | None = None
    changes: dict[str, Any] = Field(default_factory=dict)
    actor: DocumentHistoryActor | None = None
```

---

## Service Templates

### Full CRUD top-level service

```python
# pypaperless/services/widgets.py
from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.models.widgets import Widget, WidgetDraft
from . import mixins
from .base import ServiceBase


class WidgetService(
    ServiceBase,
    mixins.SecurableMixin,
    mixins.CallableMixin[Widget],
    mixins.CreatableMixin[WidgetDraft],
    mixins.IterableMixin[Widget],
    mixins.UpdatableMixin[Widget],
    mixins.DeletableMixin[Widget],
):
    """Represent a factory for Paperless `Widget` models."""

    _api_path = API_PATH["widgets"]
    _resource = PaperlessResource.WIDGETS
    _draft_cls = WidgetDraft
    _resource_cls = Widget
```

### Read-only top-level service (paginated, no write)

```python
class TrashService(ServiceBase, mixins.IterableMixin[Document]):
    _api_path = API_PATH["trash"]
    _resource = PaperlessResource.TRASH
    _resource_cls = Document

    async def restore(self, documents: list[int]) -> None:
        res = await self._client.request("post", self._api_path,
            json={"action": "restore", "documents": documents})
        res.raise_for_status()

    async def empty(self, documents: list[int] | None = None) -> None:
        payload: dict = {"action": "empty"}
        if documents is not None:
            payload["documents"] = documents
        res = await self._client.request("post", self._api_path, json=payload)
        res.raise_for_status()
```

### Document sub-service (flat list, attached pk)

```python
from typing import TYPE_CHECKING, cast
from pypaperless.exceptions import PrimaryKeyRequiredError

class DocumentHistoryService(ServiceBase):
    _api_path = API_PATH["documents_history"]
    _resource = PaperlessResource.DOCUMENTS
    _resource_cls = DocumentHistory

    def __init__(self, client: "Paperless", attached_to: int | None = None) -> None:
        super().__init__(client)
        self._attached_to = attached_to

    async def __call__(self, pk: int | None = None) -> list[DocumentHistory]:
        doc_pk = self._get_document_pk(pk)
        res = await self._client.request_json("get", self._api_path.format(pk=doc_pk))
        return [
            self._resource_cls.from_data(self._client, {**item, "document": doc_pk})
            for item in res
        ]

    def _get_document_pk(self, pk: int | None = None) -> int:
        if not any((self._attached_to, pk)):
            message = f"Accessing {type(self).__name__} data without a primary key."
            raise PrimaryKeyRequiredError(message)
        return cast(int, self._attached_to or pk)
```

---

## Document Sub-service Wiring

Sub-services attached to a `Document` instance live in their own module to avoid circular imports.
The model and service files are:

- `DocumentHistory`, `DocumentHistoryAction` — `from pypaperless.models import DocumentHistory, DocumentHistoryAction`
- `DocumentHistoryService` — `pypaperless/services/documents/history.py`
- `DocumentNote`, `DocumentNoteDraft` — `from pypaperless.models import DocumentNote, DocumentNoteDraft`
- `DocumentNoteService` — `pypaperless/services/documents/notes.py`
- `DocumentShareLinkService` — `pypaperless/services/documents/share_links.py`

### On `Document` model (direct import, no lazy init)

```python
# In models/documents/document.py — top-level imports (no circular dep because the service
# files do not import from models/documents/document.py):
from pypaperless.services.documents.history import DocumentHistoryService

# In Document class body:
_history: DocumentHistoryService | None = PrivateAttr(default=None)

@property
def history(self) -> DocumentHistoryService:
    if self._history is None:
        self._history = DocumentHistoryService(self._client, cast(int, self.id))
    return self._history
```

### On `DocumentService` (register + expose property)

```python
# In services/documents/document.py — import from the sub-service module:
from pypaperless.services.documents.history import DocumentHistoryService

# In DocumentService.__init__:
self._history = DocumentHistoryService(client)

# Property on DocumentService:
@property
def history(self) -> DocumentHistoryService:
    return self._history
```

---

## Test Fixture Shapes

### Paginated (IterableMixin resources)

```python
DATA_WIDGETS = {
    "count": 2,
    "next": None,
    "previous": None,
    "all": [1, 2],
    "results": [
        {"id": 1, "name": "Red Widget", "color": "red", ...},
        {"id": 2, "name": "Blue Widget", "color": "blue", ...},
    ],
}
```

### Flat list (document sub-services)

```python
DATA_DOCUMENT_HISTORY = [
    {"id": 10, "timestamp": "2024-01-01T00:00:00Z", "action": "update", "changes": {}, "actor": {"id": 1, "username": "admin"}},
    {"id": 1,  "timestamp": "2023-01-01T00:00:00Z", "action": "create", "changes": {}, "actor": {"id": 1, "username": "admin"}},
]
```

### Direct single object

```python
DATA_WIDGET_META = {
    "id": 42,
    "size_bytes": 1024,
    "checksum": "abc123",
}
```

---

## Audit EndpointSpec Examples

```python
# Paginated list endpoint
EndpointSpec("Widget", "/api/widgets/?page_size=1", Widget, "paginated", "Widget"),

# Single object
EndpointSpec("Config", "/api/config/1/", Config, "direct", "ApplicationConfiguration"),

# Flat list (use first element for field comparison)
EndpointSpec("DocumentNote", f"/api/documents/{TEST_DOC_ID}/notes/", DocumentNote, "list_index0", "Notes"),

# Reuses existing model (e.g. Trash returns Document objects)
EndpointSpec("Trash", "/api/trash/?page_size=1", Document, "paginated", "Document"),
```

### KNOWN_EXTRAS for injected fields

```python
KNOWN_EXTRAS["WidgetMeta"] = {
    "id": "injected by service from path parameter; not in API response",
}
KNOWN_SCHEMA_EXTRAS["WidgetMeta"] = {
    "id": "injected by service from path parameter; WidgetMeta schema has no 'id'",
}
```

---

## Mixin Reference

| Mixin               | What it adds                                                          |
| ------------------- | --------------------------------------------------------------------- |
| `CallableMixin[T]`  | `await service(pk)` — fetch single item                               |
| `IterableMixin[T]`  | `async for item in service` + `.pages()` + `.as_list()` + `.filter()` |
| `CreatableMixin[D]` | `service.create(...)` + `await service.save(draft)`                    |
| `UpdatableMixin[T]` | `await service.update(item)`                                          |
| `DeletableMixin[T]` | `await service.delete(item)`                                          |
| `SecurableMixin`    | `permissions` field + `?full_perms=true` on requests                  |

Use only the mixins the endpoint actually supports.
