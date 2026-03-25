"""Model operation dispatcher for PyPaperless."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast, get_type_hints, overload

from pypaperless.exceptions import DispatchError
from pypaperless.services.base import PaperlessService
from pypaperless.services.mixins import CreatableService, DeletableService, UpdatableService

if TYPE_CHECKING:
    from collections.abc import Callable

    from pypaperless.client import PaperlessClient
    from pypaperless.models.base import DraftLike, PaperlessModel

__all__ = ("ModelDispatcher", "dispatchable_cached_property")


_MODEL_TO_PROP_NAME: dict[type[PaperlessModel], tuple[str, ...]] = {}


def _is_writable_service(cls: type[PaperlessService]) -> bool:
    """Return True if *cls* implements any write operation (create, update, or delete)."""
    return issubclass(cls, (CreatableService, DeletableService, UpdatableService))


class DispatchableCachedProperty[ServiceT: PaperlessService]:
    """Cached-property decorator that lazily instantiates a service and registers its models.

    Works like :func:`functools.cached_property` but additionally reads the decorated
    function's ``return`` annotation to find the service class and, at class-definition
    time via :meth:`__set_name__`, registers ``_resource_cls`` and ``_draft_cls`` from
    that service class into the module-level :data:`_MODEL_TO_PROP_NAME` registry.
    This enables :class:`ModelDispatcher` to route :meth:`~ModelDispatcher.update`,
    :meth:`~ModelDispatcher.delete`, and :meth:`~ModelDispatcher.save` calls without
    the caller knowing which service to use.

    Example::

        class MyClient:
            @dispatchable_cached_property
            def correspondents(self) -> CorrespondentService:
                return CorrespondentService(self._runtime)

    """

    _attr_name: str

    def __init__(self, func: Callable[..., ServiceT]) -> None:
        """Store the factory function and copy its docstring."""
        self._func = func
        self._attr_name = ""
        self.__doc__ = func.__doc__

    def __set_name__(self, owner: type[object], name: str) -> None:
        """Cache the attribute name and register model types from the return annotation."""
        self._attr_name = name
        try:
            hints = get_type_hints(self._func)
        except (NameError, AttributeError, TypeError):
            return
        service_cls = hints.get("return")
        if not (isinstance(service_cls, type) and issubclass(service_cls, PaperlessService)):
            return
        for cls_attr in ("_resource_cls", "_draft_cls"):
            model_cls: type[PaperlessModel] | None = getattr(service_cls, cls_attr, None)
            if model_cls is not None:
                _MODEL_TO_PROP_NAME[model_cls] = (name,)
        for sub_name, attr_val in vars(service_cls).items():
            if not isinstance(attr_val, property) or attr_val.fget is None:
                continue
            try:
                sub_hints = get_type_hints(attr_val.fget)
            except (NameError, AttributeError, TypeError):
                continue
            sub_cls = sub_hints.get("return")
            if not (isinstance(sub_cls, type) and issubclass(sub_cls, PaperlessService)):
                continue
            if not _is_writable_service(sub_cls):
                continue
            for cls_attr in ("_resource_cls", "_draft_cls"):
                sub_model_cls: type[PaperlessModel] | None = getattr(sub_cls, cls_attr, None)
                if sub_model_cls is not None:
                    _MODEL_TO_PROP_NAME[sub_model_cls] = (name, sub_name)

    @overload
    def __get__(self, obj: None, objtype: type[object]) -> DispatchableCachedProperty[ServiceT]: ...

    @overload
    def __get__(self, obj: object, objtype: type[object] | None = ...) -> ServiceT: ...

    def __get__(
        self, obj: object | None, objtype: type[object] | None = None
    ) -> DispatchableCachedProperty[ServiceT] | ServiceT:
        """Return ``self`` on class access; return (and cache) the service on instance access."""
        if obj is None:
            return self
        result = self._func(obj)
        vars(obj)[self._attr_name] = result
        return result


dispatchable_cached_property = DispatchableCachedProperty


class ModelDispatcher:
    """Dispatch :meth:`update`, :meth:`delete`, and :meth:`save` to the registered service.

    :class:`ModelDispatcher` is the bridge between a :class:`~pypaperless.client.PaperlessClient`
    and its services when operating purely on model instances.  It looks up the responsible
    service from the module-level registry (populated by :class:`DispatchableCachedProperty`
    at import time) and delegates the call — without the caller needing to know which service
    to use.

    Args:
        client: The :class:`~pypaperless.client.PaperlessClient` that owns this dispatcher.

    Example::

        async with PaperlessClient("localhost:8000", "token") as paperless:
            doc = await paperless.documents(42)
            doc.title = "Renamed"
            await paperless.update(doc)          # delegates to DocumentService.update
            await paperless.delete(doc)          # delegates to DocumentService.delete
            draft = paperless.tags.create(name="invoice")
            new_id = await paperless.save(draft) # delegates to TagService.save

    """

    def __init__(self, client: PaperlessClient) -> None:
        """Store a reference to the owning client."""
        self._client = client

    def _get_service(self, model_type: type[PaperlessModel]) -> PaperlessService:
        """Return the service registered for *model_type*, or raise on unknown types."""
        path = _MODEL_TO_PROP_NAME.get(model_type)
        if path is None:
            msg = (
                f"No service registered for {model_type.__name__!r}. "
                "Only models managed by a CRUD service can be dispatched."
            )
            raise DispatchError(msg)
        obj: object = self._client
        for attr in path:
            obj = getattr(obj, attr)
        return cast("PaperlessService", obj)

    async def update(self, model: PaperlessModel, *, only_changed: bool = True) -> bool:
        """Resolve the service for *model* and delegate to its ``update`` method."""
        service = self._get_service(type(model))
        if not isinstance(service, UpdatableService):
            msg = f"Service for {type(model).__name__!r} does not support 'update'."
            raise DispatchError(msg)
        return await cast("UpdatableService[PaperlessModel]", service).update(
            model, only_changed=only_changed
        )

    async def delete(self, model: PaperlessModel, *, silent_fail: bool = False) -> None:
        """Resolve the service for *model* and delegate to its ``delete`` method."""
        service = self._get_service(type(model))
        if not isinstance(service, DeletableService):
            msg = f"Service for {type(model).__name__!r} does not support 'delete'."
            raise DispatchError(msg)
        await cast("DeletableService[PaperlessModel]", service).delete(
            model, silent_fail=silent_fail
        )

    async def save(self, draft: DraftLike) -> int | str:
        """Resolve the service for *draft* and delegate to its ``save`` method."""
        model_type = type(cast("PaperlessModel", draft))
        service = self._get_service(model_type)
        if not isinstance(service, CreatableService):
            msg = f"Service for {type(draft).__name__!r} does not support 'save'."
            raise DispatchError(msg)
        return await cast("CreatableService[PaperlessModel]", service).save(draft)
