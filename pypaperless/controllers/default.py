"""Default controllers for Paperless resources."""

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

from .base import (
    ControllerCreateFeature,
    ControllerDeleteFeature,
    ControllerListFeature,
    ControllerOneFeature,
    ControllerUpdateFeature,
)


class ConsumptionTemplatesController(
    ControllerListFeature[type[ConsumptionTemplate]],
    ControllerOneFeature[type[ConsumptionTemplate]],
):
    """Represent Paperless consumption templates resource."""

    resource: type[ConsumptionTemplate]


class CorrespondentsController(
    ControllerListFeature[type[Correspondent]],
    ControllerOneFeature[type[Correspondent]],
    ControllerCreateFeature[type[Correspondent]],
    ControllerUpdateFeature[type[Correspondent]],
    ControllerDeleteFeature[type[Correspondent]],
):
    """Represent Paperless correspondents resource."""

    resource: type[Correspondent]


class CustomFieldsController(
    ControllerListFeature[type[CustomField]],
    ControllerOneFeature[type[CustomField]],
    ControllerCreateFeature[type[CustomField]],
    ControllerUpdateFeature[type[CustomField]],
    ControllerDeleteFeature[type[CustomField]],
):
    """Represent Paperless custom fields resource."""

    resource: type[CustomField]


class DocumentTypesController(
    ControllerListFeature[type[DocumentType]],
    ControllerOneFeature[type[DocumentType]],
    ControllerCreateFeature[type[DocumentType]],
    ControllerUpdateFeature[type[DocumentType]],
    ControllerDeleteFeature[type[DocumentType]],
):
    """Represent Paperless document types resource."""

    resource: type[DocumentType]


class GroupsController(
    ControllerListFeature[type[Group]],
    ControllerOneFeature[type[Group]],
):
    """Represent Paperless groups resource."""

    resource: type[Group]


class MailAccountsController(
    ControllerListFeature[type[MailAccount]],
    ControllerOneFeature[type[MailAccount]],
):
    """Represent Paperless mail accounts resource."""

    resource: type[MailAccount]


class MailRulesController(
    ControllerListFeature[type[MailRule]],
    ControllerOneFeature[type[MailRule]],
):
    """Represent Paperless mail rules resource."""

    resource: type[MailRule]


class SavedViewsController(
    ControllerListFeature[type[SavedView]],
    ControllerOneFeature[type[SavedView]],
):
    """Represent Paperless mail rules resource."""

    resource: type[SavedView]


class ShareLinksController(
    ControllerListFeature[type[ShareLink]],
    ControllerOneFeature[type[ShareLink]],
    ControllerCreateFeature[type[ShareLink]],
    ControllerUpdateFeature[type[ShareLink]],
    ControllerDeleteFeature[type[ShareLink]],
):
    """Represent Paperless share links resource."""

    resource: type[ShareLink]


class StoragePathsController(
    ControllerListFeature[type[StoragePath]],
    ControllerOneFeature[type[StoragePath]],
    ControllerCreateFeature[type[StoragePath]],
    ControllerUpdateFeature[type[StoragePath]],
    ControllerDeleteFeature[type[StoragePath]],
):
    """Represent Paperless storage paths resource."""

    resource: type[StoragePath]


class TagsController(
    ControllerListFeature[type[Tag]],
    ControllerOneFeature[type[Tag]],
    ControllerCreateFeature[type[Tag]],
    ControllerUpdateFeature[type[Tag]],
    ControllerDeleteFeature[type[Tag]],
):
    """Represent Paperless tags resource."""

    resource: type[Tag]


class UsersController(
    ControllerListFeature[type[User]],
    ControllerOneFeature[type[User]],
):
    """Represent Paperless users resource."""

    resource: type[User]
