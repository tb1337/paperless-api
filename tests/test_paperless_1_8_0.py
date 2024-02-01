"""Paperless v1.8.0 tests."""

import pytest

from pypaperless import Paperless, PaperlessSession
from pypaperless.exceptions import DraftFieldRequired, RequestException
from pypaperless.models import Page
from pypaperless.models.mixins import helpers as helper_mixins
from pypaperless.models.mixins import models as model_mixins

from . import STORAGE_PATH_MAP, ResourceTestMapping

# mypy: ignore-errors
# pylint: disable=protected-access,redefined-outer-name


@pytest.fixture(scope="function")
async def p(api_18) -> Paperless:
    """Yield version for this test case."""
    yield api_18


# test api.py with extra storage paths endpoint
class TestBeginPaperless:
    """Paperless v1.8.0 test cases."""

    async def test_init(self, p: Paperless):
        """Test init."""
        assert isinstance(p._session, PaperlessSession)
        assert p.host_version == "1.8.0"
        assert p.is_initialized
        assert isinstance(p.local_resources, set)
        assert isinstance(p.remote_resources, set)

    async def test_resources(self, p: Paperless):
        """Test resources."""
        assert not p.config.is_available
        assert p.correspondents.is_available
        assert not p.custom_fields.is_available
        assert p.document_types.is_available
        assert p.documents.is_available
        assert p.groups.is_available
        assert p.mail_accounts.is_available
        assert p.mail_rules.is_available
        assert p.saved_views.is_available
        assert not p.share_links.is_available
        assert p.storage_paths.is_available
        assert p.tags.is_available
        assert p.users.is_available
        assert not p.workflows.is_available


@pytest.mark.parametrize(
    "mapping",
    [STORAGE_PATH_MAP],
    scope="class",
)
# test models/classifiers.py
class TestClassifiers:
    """Classifiers test cases."""

    async def test_helper(self, p: Paperless, mapping: ResourceTestMapping):
        """Test helper."""
        assert hasattr(p, mapping.resource)
        assert isinstance(getattr(p, mapping.resource), mapping.helper_cls)
        assert helper_mixins.CallableMixin in mapping.helper_cls.__bases__
        assert helper_mixins.DraftableMixin in mapping.helper_cls.__bases__
        assert helper_mixins.IterableMixin in mapping.helper_cls.__bases__

    async def test_model(self, mapping: ResourceTestMapping):
        """Test model."""
        assert model_mixins.DeletableMixin in mapping.model_cls.__bases__
        assert model_mixins.MatchingFieldsMixin in mapping.model_cls.__bases__
        assert model_mixins.PermissionFieldsMixin in mapping.model_cls.__bases__
        assert model_mixins.UpdatableMixin in mapping.model_cls.__bases__
        assert model_mixins.CreatableMixin in mapping.draft_cls.__bases__

    async def test_pages(self, p: Paperless, mapping: ResourceTestMapping):
        """Test pages."""
        page = await anext(aiter(getattr(p, mapping.resource).pages(1)))
        assert isinstance(page, Page)
        assert isinstance(page.items, list)
        for item in page.items:
            assert isinstance(item, mapping.model_cls)

    async def test_iter(self, p: Paperless, mapping: ResourceTestMapping):
        """Test iter."""
        async for item in getattr(p, mapping.resource):
            assert isinstance(item, mapping.model_cls)

    async def test_call(self, p: Paperless, mapping: ResourceTestMapping):
        """Test call."""
        item = await getattr(p, mapping.resource)(1)
        assert item
        assert isinstance(item, mapping.model_cls)
        # must raise as 1337 doesn't exist
        with pytest.raises(RequestException):
            await getattr(p, mapping.resource)(1337)

    async def test_create(self, p: Paperless, mapping: ResourceTestMapping):
        """Test create."""
        draft = getattr(p, mapping.resource).draft(**mapping.draft_defaults)
        assert isinstance(draft, mapping.draft_cls)
        backup = draft.name
        draft.name = None
        with pytest.raises(DraftFieldRequired):
            await draft.save()
        draft.name = backup
        # actually call the create endpoint
        assert await draft.save() >= 1

    async def test_udpate(self, p: Paperless, mapping: ResourceTestMapping):
        """Test update."""
        to_update = await getattr(p, mapping.resource)(5)
        new_name = f"{to_update.name} Updated"
        to_update.name = new_name
        await to_update.update()
        assert to_update.name == new_name

    async def test_delete(self, p: Paperless, mapping: ResourceTestMapping):
        """Test delete."""
        to_delete = await getattr(p, mapping.resource)(5)
        assert await to_delete.delete()
        # must raise as we deleted 5
        with pytest.raises(RequestException):
            await getattr(p, mapping.resource)(5)
