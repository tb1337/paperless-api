"""Default endpoints for Paperless resources."""

from pypaperless.models import (
    ConsumptionTemplate,
    Correspondent,
    CustomField,
    DocumentType,
    Group,
    MailAccount,
    MailRule,
    SavedView,
    ShareLink,
    StoragePath,
    Tag,
    User,
)
from pypaperless.models.shared import ResourceType

from .base import BaseEndpoint, BaseEndpointCrudMixin


class ConsumptionTemplatesEndpoint(BaseEndpoint[type[ConsumptionTemplate]]):
    """Represent Paperless consumption templates."""

    endpoint_cls = ConsumptionTemplate
    endpoint_type = ResourceType.CONSUMPTION_TEMPLATES


class CorrespondentsEndpoint(BaseEndpoint[type[Correspondent]], BaseEndpointCrudMixin):
    """Represent Paperless correspondents."""

    endpoint_cls = Correspondent
    endpoint_type = ResourceType.CORRESPONDENTS


class CustomFieldEndpoint(BaseEndpoint[type[CustomField]], BaseEndpointCrudMixin):
    """Represent Paperless custom_fields resource endpoint."""

    endpoint_cls = CustomField
    endpoint_type = ResourceType.CUSTOM_FIELDS


class DocumentTypesEndpoint(BaseEndpoint[type[DocumentType]], BaseEndpointCrudMixin):
    """Represent Paperless doctype resource endpoint."""

    endpoint_cls = DocumentType
    endpoint_type = ResourceType.DOCUMENT_TYPES


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


class ShareLinkEndpoint(BaseEndpoint[type[ShareLink]], BaseEndpointCrudMixin):
    """Represent Paperless share links."""

    endpoint_cls = ShareLink
    endpoint_type = ResourceType.SHARE_LINKS


class StoragePathsEndpoint(BaseEndpoint[type[StoragePath]], BaseEndpointCrudMixin):
    """Represent Paperless storage paths."""

    endpoint_cls = StoragePath
    endpoint_type = ResourceType.STORAGE_PATHS


class TagsEndpoint(BaseEndpoint[type[Tag]], BaseEndpointCrudMixin):
    """Represent Paperless tags."""

    endpoint_cls = Tag
    endpoint_type = ResourceType.TAGS


class UsersEndpoint(BaseEndpoint[type[User]]):
    """Represent Paperless users."""

    endpoint_cls = User
    endpoint_type = ResourceType.USERS
