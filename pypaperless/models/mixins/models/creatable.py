"""CreatableMixin for PyPaperless models."""

from typing import TYPE_CHECKING, Any, cast

from pypaperless.exceptions import DraftFieldRequiredError
from pypaperless.models.utils import object_to_dict_value

if TYPE_CHECKING:
    from pypaperless.models.base import PaperlessModelProtocol as _Base
else:
    _Base = object


class CreatableMixin(_Base):
    """Provide the `save` method for PyPaperless models."""

    _create_required_fields: set[str]

    async def save(self) -> int | str | tuple[int, int]:
        """Create a new `resource item` in Paperless.

        Return the created item `id`, or a `task_id` in case of documents.

        Example:
        -------
        ```python
        draft = paperless.documents.draft(document=bytes(...))
        draft.title = "Add a title"

        # request Paperless to store the new item
        draft.save()
        ```

        """
        self.validate_draft()
        kwdict = self._serialize()
        res = await self._api.request_json("post", self._api_path, **kwdict)

        if type(self).__name__ == "DocumentNoteDraft":
            return (
                cast("int", max(item.get("id") for item in res)),
                cast("int", kwdict["json"]["document"]),
            )
        if isinstance(res, dict):
            return int(res["id"])
        return str(res)

    def _serialize(self) -> dict[str, Any]:
        """Serialize."""
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
