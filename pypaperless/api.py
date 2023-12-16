"""Basic wrapper for each api endpoint."""

from collections.abc import Generator
from typing import TYPE_CHECKING, Any, Generic, NamedTuple, TypeVar

from aiohttp import FormData

from .models import (
    ConsumptionTemplate,
    Correspondent,
    CustomField,
    Document,
    DocumentMetaInformation,
    DocumentNote,
    DocumentPost,
    DocumentType,
    Group,
    MailAccount,
    MailRule,
    SavedView,
    ShareLink,
    StoragePath,
    Tag,
    Task,
    User,
)
from .models.base import PaperlessPost
from .models.shared import ResourceType
from .util import dataclass_from_dict, dataclass_to_dict

if TYPE_CHECKING:
    from pypaperless import Paperless

T = TypeVar("T")


class PaginatedResult(NamedTuple, Generic[T]):
    """Store a paginated result from any endpoint."""

    current_page: int
    next_page: int | None
    items: list[T]


class BaseEndpoint(Generic[T]):
    """Represent a read-only Paperless endpoint."""

    endpoint_type: ResourceType | None = None
    endpoint_cls: T | None = None

    def __init__(self, paperless: "Paperless", endpoint) -> None:
        """Initialize endpoint."""
        self._paperless = paperless
        self._endpoint = endpoint
        self.logger = paperless.logger.getChild(self.endpoint_type)

    async def list(self) -> list[int] | None:
        """Return a list of all entity ids, if applicable."""
        res = await self._paperless.request("get", self._endpoint)
        if "all" in res:
            return [*res["all"]]

        self.logger.debug("List result is empty.")

    async def get(
        self,
        **kwargs: dict[str, Any],
    ) -> PaginatedResult[T]:
        """
        Request api pages as list.

        Set a `page` parameter to request any desired page in results.
        If `page` is omitted, page 1 will be requested.

        Example:
            paperless.endpoint.get(): Results in requesting page 1
            paperless.endpoint.get(`page`=2): Page 2 will be requested
        """
        if "page" not in kwargs:
            kwargs["page"] = 1
        res = await self._paperless.request("get", self._endpoint, params=kwargs)
        return PaginatedResult(
            kwargs["page"],
            kwargs["page"] + 1 if res["next"] else None,
            [dataclass_from_dict(self.endpoint_cls, item) for item in res["results"]],
        )

    async def iterate(self, **kwargs: dict[str, Any]) -> Generator[T, None, None]:
        """Iterate pages and yield every entity."""
        page = 1
        while page:
            kwargs["page"] = page
            res = await self.get(**kwargs)
            page = res.next_page
            for item in res.items:
                yield item

    async def one(self, idx: int) -> T:
        """Request exactly one entity by id."""
        endpoint = f"{self._endpoint}{idx}/"
        res = await self._paperless.request("get", endpoint)
        return dataclass_from_dict(self.endpoint_cls, res)


class EndpointCUDMixin:
    """Mixin that adds basic CUD features to endpoints."""

    async def create(self, item: PaperlessPost) -> T:
        """Create a new entity. Raise on failure."""
        res = await self._paperless.request("post", self._endpoint, json=dataclass_to_dict(item))
        return dataclass_from_dict(self._cls, res)

    async def update(self, item: T) -> T:
        """Update an existing entity. Raise on failure."""
        endpoint = f"{self._endpoint}{item.id}/"
        res = await self._paperless.request(
            "put", endpoint, json=dataclass_to_dict(item, skip_none=False)
        )
        return dataclass_from_dict(self._cls, res)

    async def delete(self, item: T) -> bool:
        """Delete an existing entity. Raise on failure."""
        endpoint = f"{self._endpoint}{item.id}/"
        await self._paperless.request("delete", endpoint)
        return True


class ConsumptionTemplatesEndpoint(BaseEndpoint[type[ConsumptionTemplate]]):
    """Represent Paperless consumption templates."""

    endpoint_cls = ConsumptionTemplate
    endpoint_type = ResourceType.CONSUMPTION_TEMPLATES


class CorrespondentsEndpoint(BaseEndpoint[type[Correspondent]], EndpointCUDMixin):
    """Represent Paperless correspondents."""

    endpoint_cls = Correspondent
    endpoint_type = ResourceType.CORRESPONDENTS


class CustomFieldEndpoint(BaseEndpoint[type[CustomField]], EndpointCUDMixin):
    """Represent Paperless custom_fields resource endpoint."""

    endpoint_cls = CustomField
    endpoint_type = ResourceType.CUSTOM_FIELDS


class DocumentTypesEndpoint(BaseEndpoint[type[DocumentType]], EndpointCUDMixin):
    """Represent Paperless doctype resource endpoint."""

    endpoint_cls = DocumentType
    endpoint_type = ResourceType.DOCUMENT_TYPES


class DocumentsEndpoint(BaseEndpoint[type[Document]], EndpointCUDMixin):
    """Represent Paperless document resource endpoint."""

    endpoint_cls = Document
    endpoint_type = ResourceType.DOCUMENTS

    async def create(self, item: DocumentPost) -> str:
        """Create a new document. Raise on failure."""
        form = FormData()

        form.add_field("document", item.document)

        for field in [
            "document",
            "title",
            "created",
            "correspondent",
            "document_type",
            "archive_serial_number",
        ]:
            if item[field]:
                form.add_field(field, item[field])

        if item.tags and isinstance(item.tags, list):
            for tag in item.tags:
                form.add_field("tags", f"{tag}")

        endpoint = f"{self._endpoint}post_document/"
        res = await self._paperless.request("post", endpoint, data=form)
        return str(res)

    def _get_item_id(self, item) -> int:
        if isinstance(item, Document):
            return item.id
        return item

    async def _request_child_endpoint(
        self,
        path: str,
        item: Document | int,
    ):
        """Download the document source file."""
        idx = self._get_item_id(item)
        endpoint = f"{self._endpoint}{idx}/{path}/"
        res = await self._paperless.request("get", endpoint)
        return res

    async def metadata(self, item: Document | int) -> T:
        """Request document metadata of given document."""
        res = await self._request_child_endpoint("metadata", item)
        return dataclass_from_dict(DocumentMetaInformation, res)

    async def download(self, item: Document | int) -> bytearray:
        """Request document endpoint for downloading the actual file."""
        return await self._request_child_endpoint("download", item)

    async def preview(self, item: Document | int) -> bytearray:
        """Request document endpoint for previewing the actual file."""
        return await self._request_child_endpoint("preview", item)

    async def thumb(self, item: Document | int) -> bytearray:
        """Request document endpoint for the thumbnail file."""
        return await self._request_child_endpoint("thumb", item)

    async def notes(self, item: Document | int) -> T:
        """Request document notes of given document."""
        idx = self._get_item_id(item)
        endpoint = f"{self._endpoint}{idx}/notes/"
        res = await self._paperless.request("get", endpoint)
        return [dataclass_from_dict(DocumentNote, {**item, "document": idx}) for item in res]


class GroupsEndpoint(BaseEndpoint[type[Group]]):
    """Represent Paperless users."""

    endpoint_cls = Group
    endpoint_type = ResourceType.GROUPS


class MailAccountsEndpoint(BaseEndpoint[type[MailAccount]]):
    """Represent Paperless mail accounts."""

    endpoint_cls = MailAccount
    endpoint_type = ResourceType.MAIL_ACCOUNTS


class MailRulesEndpoint(BaseEndpoint[type[MailRule]]):
    """Represent Paperless mail rules."""

    endpoint_cls = MailRule
    endpoint_type = ResourceType.MAIL_RULES


class SavedViewsEndpoint(BaseEndpoint[type[SavedView]]):
    """Represent Paperless saved views."""

    endpoint_cls = SavedView
    endpoint_type = ResourceType.SAVED_VIEWS


class ShareLinkEndpoint(BaseEndpoint[type[ShareLink]], EndpointCUDMixin):
    """Represent Paperless share links."""

    endpoint_cls = ShareLink
    endpoint_type = ResourceType.SHARE_LINKS


class StoragePathsEndpoint(BaseEndpoint[type[StoragePath]], EndpointCUDMixin):
    """Represent Paperless storage paths."""

    endpoint_cls = StoragePath
    endpoint_type = ResourceType.STORAGE_PATHS


class TagsEndpoint(BaseEndpoint[type[Tag]], EndpointCUDMixin):
    """Represent Paperless tags."""

    endpoint_cls = Tag
    endpoint_type = ResourceType.TAGS


class TasksEndpoint(BaseEndpoint[type[Task]]):
    """Represent Paperless tasks."""

    endpoint_cls = Task
    endpoint_type = ResourceType.TASKS

    # this endpoint inherits list() from BaseEndpoint
    # TODO: we have to do something about it, as tasks have no all-attribute in result json
    async def get(
        self,
        **kwargs: dict[str, Any],
    ) -> list[T]:
        """Request entities."""
        res = await self._paperless.request("get", self._endpoint, params=kwargs)
        return [dataclass_from_dict(self.endpoint_cls, item) for item in res]

    async def one(self, idx: str) -> T:
        """Request exactly one entity by id."""
        res = await self._paperless.request("get", self._endpoint, params={"task_id": idx})
        return dataclass_from_dict(self.endpoint_cls, res.pop())


class UsersEndpoint(BaseEndpoint[type[User]]):
    """Represent Paperless users."""

    endpoint_cls = User
    endpoint_type = ResourceType.USERS
