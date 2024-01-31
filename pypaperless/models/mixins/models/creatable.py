"""CreatableMixin for PyPaperless models."""

from typing import cast, final

from pypaperless.exceptions import DraftFieldRequired
from pypaperless.models.base import PaperlessModelProtocol
from pypaperless.models.utils import object_to_dict_value


class CreatableMixin(PaperlessModelProtocol):  # pylint: disable=too-few-public-methods
    """Provide the `save` method for PyPaperless models."""

    _create_required_fields: set[str]

    @final
    async def save(self) -> int | str | tuple[int, int]:
        """Create a new `resource item` in Paperless.

        Return the created item `id`, or a `task_id` in case of documents.

        Example:
        ```python
        draft = paperless.documents.draft(document=bytes(...))
        draft.title = "Add a title"

        # request Paperless to store the new item
        draft.save()
        ```
        """
        self.validate()

        # in case of DocumentDraft, we want to transmit data as form
        # this is kind of dirty, but should do its job in this case
        as_form = type(self).__name__ == "DocumentDraft"
        kwargs = {
            "form" if as_form else "json": {
                field.name: object_to_dict_value(getattr(self, field.name))
                for field in self._get_dataclass_fields()
            }
        }
        res = await self._api.request_json("post", self._api_path, **kwargs)

        if type(self).__name__ == "DocumentNoteDraft":
            return (
                cast(int, max(item.get("id") for item in res)),
                cast(int, kwargs["json"]["document"]),
            )
        if isinstance(res, dict):
            return int(res["id"])
        return str(res)

    @final
    def validate(self) -> None:
        """Check required fields before persisting the item to Paperless."""
        missing = [field for field in self._create_required_fields if getattr(self, field) is None]

        if len(missing) == 0:
            return
        raise DraftFieldRequired(
            f"Missing fields for saving a `{self.__class__.__name__}`: {', '.join(missing)}."
        )
