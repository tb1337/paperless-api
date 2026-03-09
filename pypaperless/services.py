"""PyPaperless services."""

# pylint: disable=unused-import

from .models.base import ServiceBase  # noqa: F401
from .models.classifiers import (  # noqa: F401
    CorrespondentService,
    DocumentTypeService,
    StoragePathService,
    TagService,
)
from .models.config import ConfigService  # noqa: F401
from .models.custom_fields import CustomFieldService  # noqa: F401
from .models.documents import DocumentService, DocumentMetaService, DocumentNoteService  # noqa: F401
from .models.mails import MailAccountService, MailRuleService, ProcessedMailService  # noqa: F401
from .models.permissions import GroupService, UserService  # noqa: F401
from .models.remote_version import RemoteVersionService  # noqa: F401
from .models.saved_views import SavedViewService  # noqa: F401
from .models.share_links import ShareLinkService  # noqa: F401
from .models.statistics import StatisticService  # noqa: F401
from .models.status import StatusService  # noqa: F401
from .models.tasks import TaskService  # noqa: F401
from .models.workflows import WorkflowService  # noqa: F401
