"""Paperless v2.3.0 tests."""

import pytest

import pypaperless.models.workflows as wf_helpers
from pypaperless import Paperless, PaperlessSession
from pypaperless.exceptions import RequestException
from pypaperless.models import Page, WorkflowAction, WorkflowTrigger
from pypaperless.models.mixins import helpers as helper_mixins
from pypaperless.models.mixins import models as model_mixins

from . import WORKFLOW_MAP, ResourceTestMapping

# mypy: ignore-errors
# pylint: disable=protected-access,redefined-outer-name


@pytest.fixture(scope="function")
async def p(api_23) -> Paperless:
    """Yield version for this test case."""
    yield api_23


# test api.py with extra workflows endpoint
class TestBeginPaperless:
    """Paperless v2.3.0 test cases."""

    async def test_init(self, p: Paperless):
        """Test init."""
        assert isinstance(p._session, PaperlessSession)
        assert p.host_version == "2.3.0"
        assert p.is_initialized
        assert isinstance(p.local_resources, set)
        assert isinstance(p.remote_resources, set)

    async def test_resources(self, p: Paperless):
        """Test resources."""
        assert p.correspondents.is_available
        assert p.custom_fields.is_available
        assert p.document_types.is_available
        assert p.documents.is_available
        assert p.groups.is_available
        assert p.mail_accounts.is_available
        assert p.mail_rules.is_available
        assert p.saved_views.is_available
        assert p.share_links.is_available
        assert p.storage_paths.is_available
        assert p.tags.is_available
        assert p.users.is_available
        assert p.workflows.is_available


@pytest.mark.parametrize(
    "mapping",
    [WORKFLOW_MAP],
    scope="class",
)
# test models/workflows.py
class TestWorkflows:
    """Read only resources test cases."""

    async def test_helper(self, p: Paperless, mapping: ResourceTestMapping):
        """Test helper."""
        assert hasattr(p, mapping.resource)
        assert isinstance(getattr(p, mapping.resource), mapping.helper_cls)
        assert helper_mixins.CallableMixin in mapping.helper_cls.__bases__
        assert helper_mixins.DraftableMixin not in mapping.helper_cls.__bases__
        assert helper_mixins.IterableMixin in mapping.helper_cls.__bases__
        # test sub helpers
        assert isinstance(p.workflows.actions, wf_helpers.WorkflowActionHelper)
        assert isinstance(p.workflows.triggers, wf_helpers.WorkflowTriggerHelper)

    async def test_model(self, mapping: ResourceTestMapping):
        """Test model."""
        for model_cls in (
            mapping.model_cls,
            WorkflowAction,
            WorkflowTrigger,
        ):
            assert model_mixins.DeletableMixin not in model_cls.__bases__
            assert model_mixins.PermissionFieldsMixin not in model_cls.__bases__
            assert model_mixins.UpdatableMixin not in model_cls.__bases__

            matching = model_mixins.MatchingFieldsMixin in model_cls.__bases__
            if model_cls is WorkflowTrigger:
                assert matching
            else:
                assert not matching

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
        # check underlying model lists
        assert isinstance(item.actions, list)
        for a in item.actions:
            assert isinstance(a, WorkflowAction)
        assert isinstance(item.triggers, list)
        for t in item.triggers:
            assert isinstance(t, WorkflowTrigger)
