"""PyPaperless services."""

from .base import ResourceService  # noqa: F401
from .cache import CacheService  # noqa: F401
from .config import ConfigService  # noqa: F401
from .correspondents import CorrespondentService  # noqa: F401
from .custom_fields import CustomFieldService  # noqa: F401
from .document_types import DocumentTypeService  # noqa: F401
from .documents.document import DocumentMetaService, DocumentService  # noqa: F401
from .documents.notes import DocumentNoteService  # noqa: F401
from .mails import MailAccountService, MailRuleService, ProcessedMailService  # noqa: F401
from .permissions import GroupService, UserService  # noqa: F401
from .profile import ProfileService  # noqa: F401
from .remote_version import RemoteVersionService  # noqa: F401
from .saved_views import SavedViewService  # noqa: F401
from .share_links import ShareLinkService  # noqa: F401
from .statistics import StatisticService  # noqa: F401
from .status import StatusService  # noqa: F401
from .storage_paths import StoragePathService  # noqa: F401
from .tags import TagService  # noqa: F401
from .tasks import TaskService  # noqa: F401
from .trash import TrashService  # noqa: F401
from .workflows import WorkflowService  # noqa: F401
