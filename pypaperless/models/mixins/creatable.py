"""CreatableModel for PyPaperless models."""

from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict

from pypaperless.exceptions import DraftFieldRequiredError


class CreatableModel(BaseModel):
    """Provide draft validation and serialization for PyPaperless models.

    Draft models forbid unknown fields: a typo in a ``create()`` keyword
    argument raises a :exc:`pydantic.ValidationError` immediately instead of
    being silently dropped.
    """

    model_config = ConfigDict(extra="forbid")

    _create_required_fields: ClassVar[set[str]]

    def serialize(self) -> dict[str, Any]:
        """Serialize draft fields for API submission."""
        payload = self.model_dump(mode="json", by_alias=True)
        # empty permissions raise server-side, so drop the field when unset
        if payload.get("set_permissions") is None:
            payload.pop("set_permissions", None)

        return {"json": payload}

    def validate_draft(self) -> None:
        """Check required fields before persisting the item to Paperless."""
        missing = [field for field in self._create_required_fields if getattr(self, field) is None]

        if not missing:
            return

        message = f"Missing fields for saving a `{type(self).__name__}`: {', '.join(missing)}."
        raise DraftFieldRequiredError(message)
