"""Model for consumption template resource."""

from dataclasses import dataclass

from .base import PaperlessModel
from .shared import ConsumptionTemplateSource


@dataclass(kw_only=True)
class ConsumptionTemplate(PaperlessModel):  # pylint: disable=too-many-instance-attributes
    """Represent a consumption template resource on the Paperless api."""

    id: int | None = None
    name: str | None = None
    order: int | None = None
    sources: list[ConsumptionTemplateSource] | None = None
    filter_path: str | None = None
    filter_filename: str | None = None
    filter_mailrule: int | None = None
    assign_title: str | None = None
    assign_tags: list[int] | None = None
    assign_correspondent: int | None = None
    assign_document_type: int | None = None
    assign_storage_path: int | None = None
    assign_owner: int | None = None
    assign_view_users: list[int] | None = None
    assign_view_groups: list[int] | None = None
    assign_change_users: list[int] | None = None
    assign_change_groups: list[int] | None = None
    assign_custom_fields: list[int] | None = None
