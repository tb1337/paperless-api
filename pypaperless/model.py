from dataclasses import dataclass, field
from typing import List

from datetime import datetime


__all__ = [
    "PaperlessCorrespondent",
    "PaperlessDocumentType",
    "PaperlessTag",
    "PaperlessSavedView",
    "PaperlessDocumentNote",
    "PaperlessDocument",
    "PaperlessTask",
    "PaperlessStoragePath",
    "PaperlessUser",
    "PaperlessGroup",
    "PaperlessMailAccount",
    "PaperlessMailRule",
    "PaperlessModel",
    "PaperlessCustomField"
]


ENDPOINT_USERS = "users"
ENDPOINT_CORRESPONDENTS = "correspondents"
ENDPOINT_DOCUMENT_TYPES = "document_types"
ENDPOINT_TAGS = "tags"
ENDPOINT_SAVED_VIEWS = "saved_views"
ENDPOINT_DOCUMENTS = "documents"
ENDPOINT_TASKS = "tasks"
ENDPOINT_STORAGE_PATHS = "storage_paths"
ENDPOINT_GROUPS = "groups"
ENDPOINT_MAIL_ACCOUNTS = "mail_accounts"
ENDPOINT_MAIL_RULES = "mail_rules"
ENDPOINT_CUSTOM_FIELDS = "custom_fields"

ENDPOINT_SUFFIX_NOTES = "notes"


def datetime_field_factory():
    return datetime.now()


class PaperlessModel:
    _endpoint: str = None
    _endpoint_suffix: str = ""


@dataclass(kw_only=True)
class PaperlessCustomField(PaperlessModel):
    """
    Class that represents a custom field in the paperless API
    """

    _endpoint: str = ENDPOINT_CUSTOM_FIELDS
    id: int = None
    name: str
    data_type: str


@dataclass(kw_only=True)
class PaperlessUser(PaperlessModel):
    """
    Class that represents a user object in the paperless API
    """

    _endpoint: str = ENDPOINT_USERS
    id: int = None
    username: str
    password: str
    email: str
    first_name: str
    last_name: str
    date_joined: datetime = field(default_factory=datetime_field_factory)
    last_login: datetime = None
    is_staff: bool = True
    is_active: bool = True
    is_superuser: bool = False
    groups: List[int] = field(default_factory=list)
    user_permissions: List[str] = field(default_factory=list)
    inherited_permissions: List[str] = None


@dataclass(kw_only=True)
class PaperlessCorrespondent(PaperlessModel):
    """
    Class that represents a document type object in the paperless API.
    """

    _endpoint: str = ENDPOINT_CORRESPONDENTS
    id: int = None
    slug: str = None
    name: str
    match: str = ""
    matching_algorithm: int = 0
    is_insensitive: bool = True
    document_count: int = None
    last_correspondence: datetime = None
    owner: int = None
    user_can_change: bool = None


@dataclass(kw_only=True)
class PaperlessDocumentType(PaperlessModel):
    """
    Class that represents a document type object in the paperless API.
    """

    _endpoint: str = ENDPOINT_DOCUMENT_TYPES
    id: int = None
    slug: str = None
    name: str
    match: str = ""
    matching_algorithm: int = 0
    is_insensitive: bool = True
    document_count: int = None
    owner: int = None
    user_can_change: bool = None


@dataclass(kw_only=True)
class PaperlessTag(PaperlessModel):
    """
    Class that represents a tag object in the paperless API.
    """

    _endpoint: str = ENDPOINT_TAGS
    id: int = None
    slug: str = None
    name: str
    colour: int = 1
    match: str = ""
    matching_algorithm: int = 0
    is_insensitive: bool = True
    is_inbox_tag: bool = False
    document_count: int = None
    owner: int = None
    user_can_change: bool = None
    color: str
    text_color: str


@dataclass(kw_only=True)
class PaperlessSavedView(PaperlessModel):
    """
    Class that represents a saved view object in the paperless API.
    """

    _endpoint: str = ENDPOINT_SAVED_VIEWS
    id: int = None
    name: str
    show_on_dashboard: bool = False
    show_in_sidebar: bool = False
    sort_field: str = None
    sort_reverse: bool = False
    filter_rules: List[dict] = field(default_factory=list)
    owner: PaperlessUser = None
    user_can_change: bool = None

    def __post_init__(self):
        if self.owner:
            self.owner = PaperlessUser(**self.owner)


@dataclass(kw_only=True)
class PaperlessDocumentNote(PaperlessModel):
    """
    Class that respresents a document note in the paperless API
    """

    _endpoint: str = ENDPOINT_DOCUMENTS
    _endpoint_suffix: str = ENDPOINT_SUFFIX_NOTES
    id: int = None
    note: str
    created: datetime = None
    document: int
    user: int = None


@dataclass(kw_only=True)
class PaperlessDocument(PaperlessModel):
    """
    Class that represents a document object in the paperless API.
    """

    _endpoint: str = ENDPOINT_DOCUMENTS
    id: int
    correspondent: int
    document_type: int
    storage_path: int
    title: str
    content: str
    tags: List[int]
    created: datetime
    created_date: datetime
    modified: datetime
    added: datetime
    archive_serial_number: int
    original_file_name: str
    archived_file_name: str
    owner: int
    user_can_change: bool
    notes: List[PaperlessDocumentNote]
    custom_fields: List[PaperlessCustomField]

    def __post_init__(self):
        self.notes = [PaperlessDocumentNote(**item) for item in self.notes]


@dataclass(kw_only=True)
class PaperlessTask(PaperlessModel):
    """
    Class that represents a task object in the paperless API
    """

    _endpoint: str = ENDPOINT_TASKS
    id: int
    task_id: str
    task_file_name: str
    date_created: datetime
    date_done: datetime
    type: str
    status: str
    result: str
    acknowledged: bool
    related_document: int


@dataclass(kw_only=True)
class PaperlessStoragePath(PaperlessModel):
    """
    Class that represents a storage path object in the paperless API
    """

    _endpoint: str = ENDPOINT_STORAGE_PATHS
    id: int = None
    slug: str = None
    name: str
    path: str
    match: str = ""
    matching_algorithm: int = 0
    is_insensitive: bool = True
    document_count: int = None
    owner: int = None
    user_can_change: bool = None


@dataclass(kw_only=True)
class PaperlessGroup(PaperlessModel):
    """
    Class that represents a group object in the paperless API
    """

    _endpoint: str = ENDPOINT_GROUPS
    id: int = None
    name: str
    permissions: List[str] = field(default_factory=list)


@dataclass(kw_only=True)
class PaperlessMailAccount(PaperlessModel):
    """
    Class that represents a mail account object in the paperless API
    """

    _endpoint: str = ENDPOINT_MAIL_ACCOUNTS
    id: int = None
    name: str
    imap_server: str
    imap_port: int
    imap_security: int
    username: str
    password: str
    character_set: str
    is_token: bool
    owner: int = None
    user_can_change: bool = None


@dataclass(kw_only=True)
class PaperlessMailRule(PaperlessModel):
    """
    Class that represents a mail rule object in the paperless API
    """

    _endpoint: str = ENDPOINT_MAIL_RULES
    id: int = None
    name: str
    account: int
    folder: str
    filter_from: str
    filter_to: str
    filter_subject: str
    filter_body: str
    filter_attachment_filename: str
    maximum_age: int
    action: int
    action_parameter: str
    assign_title_from: int
    assign_tags: List[int]
    assign_correspondent_from: int
    assign_correspondent: int
    assign_document_type: int
    order: int
    attachment_type: int
    consumption_scope: int
    owner: int = None
    user_can_change: bool = None
