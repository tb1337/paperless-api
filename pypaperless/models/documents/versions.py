"""Provide `DocumentVersionInfo` and `DocumentRoot` models."""

import datetime
from typing import ClassVar

from pypaperless.const import EndpointPath
from pypaperless.models.base import PaperlessModel


class DocumentVersionInfo(PaperlessModel):
    """Represent version metadata for a Paperless `Document`."""

    id: int | None = None
    added: datetime.datetime | None = None
    version_label: str | None = None
    checksum: str | None = None
    is_root: bool | None = None


class DocumentRoot(PaperlessModel):
    """Represent the root-document response for a Paperless `Document`."""

    _api_path: ClassVar[str] = EndpointPath.DOCUMENTS_ROOT

    root_id: int | None = None
