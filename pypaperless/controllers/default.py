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
    Workflow,
    WorkflowAction,
    WorkflowTrigger,
)

from .base import (
    BaseController,
    CreateMixin,
    DeleteMixin,
    ListMixin,
    OneMixin,
    PaginationMixin,
    UpdateMixin,
)


class ConsumptionTemplatesController(
    BaseController[ConsumptionTemplate],
    PaginationMixin[ConsumptionTemplate],
    ListMixin[ConsumptionTemplate],
    OneMixin[ConsumptionTemplate],
):
    """Represent Paperless consumption templates resource."""

    _resource = ConsumptionTemplate


class CorrespondentsController(  # pylint: disable=too-many-ancestors
    BaseController[Correspondent],
    PaginationMixin[Correspondent],
    ListMixin[Correspondent],
    OneMixin[Correspondent],
    CreateMixin[Correspondent],
    UpdateMixin[Correspondent],
    DeleteMixin[Correspondent],
):
    """Represent Paperless correspondents resource."""

    _resource = Correspondent


class CustomFieldsController(  # pylint: disable=too-many-ancestors
    BaseController[CustomField],
    PaginationMixin[CustomField],
    ListMixin[CustomField],
    OneMixin[CustomField],
    CreateMixin[CustomField],
    UpdateMixin[CustomField],
    DeleteMixin[CustomField],
):
    """Represent Paperless custom fields resource."""

    _resource = CustomField


class DocumentTypesController(  # pylint: disable=too-many-ancestors
    BaseController[DocumentType],
    PaginationMixin[DocumentType],
    ListMixin[DocumentType],
    OneMixin[DocumentType],
    CreateMixin[DocumentType],
    UpdateMixin[DocumentType],
    DeleteMixin[DocumentType],
):
    """Represent Paperless document types resource."""

    _resource = DocumentType


class GroupsController(
    BaseController[Group],
    PaginationMixin[Group],
    ListMixin[Group],
    OneMixin[Group],
):
    """Represent Paperless groups resource."""

    _resource = Group


class MailAccountsController(
    BaseController[MailAccount],
    PaginationMixin[MailAccount],
    ListMixin[MailAccount],
    OneMixin[MailAccount],
):
    """Represent Paperless mail accounts resource."""

    _resource = MailAccount


class MailRulesController(
    BaseController[MailRule],
    PaginationMixin[MailRule],
    ListMixin[MailRule],
    OneMixin[MailRule],
):
    """Represent Paperless mail rules resource."""

    _resource = MailRule


class SavedViewsController(
    BaseController[SavedView],
    PaginationMixin[SavedView],
    ListMixin[SavedView],
    OneMixin[SavedView],
):
    """Represent Paperless mail rules resource."""

    _resource = SavedView


class ShareLinksController(  # pylint: disable=too-many-ancestors
    BaseController[ShareLink],
    PaginationMixin[ShareLink],
    ListMixin[ShareLink],
    OneMixin[ShareLink],
    CreateMixin[ShareLink],
    UpdateMixin[ShareLink],
    DeleteMixin[ShareLink],
):
    """Represent Paperless share links resource."""

    _resource = ShareLink


class StoragePathsController(  # pylint: disable=too-many-ancestors
    BaseController[StoragePath],
    PaginationMixin[StoragePath],
    ListMixin[StoragePath],
    OneMixin[StoragePath],
    CreateMixin[StoragePath],
    UpdateMixin[StoragePath],
    DeleteMixin[StoragePath],
):
    """Represent Paperless storage paths resource."""

    _resource = StoragePath


class TagsController(  # pylint: disable=too-many-ancestors
    BaseController[Tag],
    PaginationMixin[Tag],
    ListMixin[Tag],
    OneMixin[Tag],
    CreateMixin[Tag],
    UpdateMixin[Tag],
    DeleteMixin[Tag],
):
    """Represent Paperless tags resource."""

    _resource = Tag


class UsersController(
    BaseController[User],
    PaginationMixin[User],
    ListMixin[User],
    OneMixin[User],
):
    """Represent Paperless users resource."""

    _resource = User


class WorkflowsController(
    BaseController[Workflow],
    PaginationMixin[Workflow],
    ListMixin[Workflow],
    OneMixin[Workflow],
):
    """Represent Paperless workflows resource."""

    _resource = Workflow


class WorkflowActionsController(
    BaseController[WorkflowAction],
    PaginationMixin[WorkflowAction],
    ListMixin[WorkflowAction],
    OneMixin[WorkflowAction],
):
    """Represent Paperless workflow actions resource."""

    _resource = WorkflowAction


class WorkflowTriggersController(
    BaseController[WorkflowTrigger],
    PaginationMixin[WorkflowTrigger],
    ListMixin[WorkflowTrigger],
    OneMixin[WorkflowTrigger],
):
    """Represent Paperless workflow triggers resource."""

    _resource = WorkflowTrigger
