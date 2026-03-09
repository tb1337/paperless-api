"""CreatableMixin for PyPaperless models."""

from typing import Any, ClassVar

from pypaperless.exceptions import DraftFieldRequiredError
from pypaperless.models.utils import object_to_dict_value


class CreatableMixin:
    """Provide draft validation and serialization for PyPaperless models."""

    _create_required_fields: ClassVar[set[str]]
    model_fields: ClassVar[dict[str, Any]]  # provided by BaseModel

    def _serialize(self) -> dict[str, Any]:
        """Serialize draft fields for API submission."""
        data = {
            "json": {
                name: object_to_dict_value(getattr(self, name))
                for name in self.__class__.model_fields
            },
        }
        # check for empty permissions as they will raise if None
        if "set_permissions" in data["json"] and data["json"]["set_permissions"] is None:
            del data["json"]["set_permissions"]

        return data

    def validate_draft(self) -> None:
        """Check required fields before persisting the item to Paperless."""
        missing = [field for field in self._create_required_fields if getattr(self, field) is None]

        if len(missing) == 0:
            return

        message = f"Missing fields for saving a `{type(self).__name__}`: {', '.join(missing)}."
        raise DraftFieldRequiredError(message)
