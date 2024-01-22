"""CreatableMixin for PyPaperless models."""

from typing import final

from pypaperless.errors import DraftFieldRequired
from pypaperless.models.base import PaperlessModelProtocol
from pypaperless.util import object_to_dict_value


class CreatableMixin(PaperlessModelProtocol):  # pylint: disable=too-few-public-methods
    """Provide the `save` method for PyPaperless models."""

    _create_required_fields: set[str]

    @final
    async def save(self) -> int | str:
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
            "form"
            if as_form
            else "json": {
                field.name: object_to_dict_value(getattr(self, field.name))
                for field in self._get_dataclass_fields()
            }
        }
        res = await self._api.request_json("post", self._api_path, **kwargs)

        if isinstance(res, dict):
            return int(res["id"])
        return str(res)

    @final
    def validate(self) -> None:
        """Check required fields before persisting the item to Paperless."""
        for field in self._create_required_fields:
            if getattr(self, field) is None:
                raise DraftFieldRequired(
                    f"Field `{field}` is required for saving a `{self.__class__.__name__}`."
                )
