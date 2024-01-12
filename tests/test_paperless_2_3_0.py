"""Paperless v2.3.0 tests."""

import pytest
from aiohttp.web_exceptions import HTTPNotFound

from pypaperless import Paperless
from pypaperless.const import PaperlessFeature
from pypaperless.controllers import (
    WorkflowActionsController,
    WorkflowsController,
    WorkflowTriggersController,
)
from pypaperless.controllers.base import ResultPage
from pypaperless.models import Workflow, WorkflowAction, WorkflowTrigger
from pypaperless.models.workflows import (
    WorkflowActionType,
    WorkflowTriggerSource,
    WorkflowTriggerType,
)


class TestBeginPaperless:
    """Paperless v2.3.0 test cases."""

    async def test_init(self, api_23: Paperless):
        """Test init."""
        assert api_23._token
        assert api_23._request_opts
        assert not api_23._session
        # test properties
        assert api_23.url
        assert api_23.is_initialized

    async def test_features(self, api_23: Paperless):
        """Test features."""
        # basic class has no features
        assert PaperlessFeature.CONTROLLER_STORAGE_PATHS in api_23.features
        assert PaperlessFeature.FEATURE_DOCUMENT_NOTES in api_23.features
        assert PaperlessFeature.CONTROLLER_SHARE_LINKS in api_23.features
        assert PaperlessFeature.CONTROLLER_CUSTOM_FIELDS in api_23.features
        assert PaperlessFeature.CONTROLLER_WORKFLOWS in api_23.features
        assert (
            PaperlessFeature.CONTROLLER_CONSUMPTION_TEMPLATES not in api_23.features
        )  # got removed again
        assert api_23.storage_paths
        assert api_23.custom_fields
        assert api_23.share_links
        assert api_23.workflows
        assert api_23.workflow_actions
        assert api_23.workflow_triggers
        assert not api_23.consumption_templates  # got removed again

    async def test_enums(self):
        """Test enums."""
        assert WorkflowActionType(999) == WorkflowActionType.UNKNOWN
        assert WorkflowTriggerSource(999) == WorkflowTriggerSource.UNKNOWN
        assert WorkflowTriggerType(999) == WorkflowTriggerType.UNKNOWN


class TestWorkflows:
    """Workflows test cases."""

    async def test_controller(self, api_23: Paperless):
        """Test controller."""
        assert isinstance(api_23.workflows, WorkflowsController)
        # test mixins
        assert hasattr(api_23.workflows, "list")
        assert hasattr(api_23.workflows, "get")
        assert hasattr(api_23.workflows, "iterate")
        assert hasattr(api_23.workflows, "one")
        assert not hasattr(api_23.workflows, "create")
        assert not hasattr(api_23.workflows, "update")
        assert not hasattr(api_23.workflows, "delete")

    async def test_list(self, api_23: Paperless):
        """Test list."""
        items = await api_23.workflows.list()
        assert isinstance(items, list)
        assert len(items) > 0
        for item in items:
            assert isinstance(item, int)

    async def test_get(self, api_23: Paperless):
        """Test get."""
        results = await api_23.workflows.get()
        assert isinstance(results, ResultPage)
        assert results.current_page == 1
        assert not results.next_page  # there is 1 page in sample data
        assert results.last_page == 1  # there is 1 page in sample data
        assert isinstance(results.items, list)
        for item in results.items:
            assert isinstance(item, Workflow)

    async def test_iterate(self, api_23: Paperless):
        """Test iterate."""
        async for item in api_23.workflows.iterate():
            assert isinstance(item, Workflow)

    async def test_one(self, api_23: Paperless):
        """Test one."""
        item = await api_23.workflows.one(1)
        assert item
        assert isinstance(item, Workflow)
        # must raise as 1337 doesn't exist
        with pytest.raises(HTTPNotFound):
            await api_23.workflows.one(1337)


class TestWorkflowsAction:
    """Workflow Actions test cases."""

    async def test_controller(self, api_23: Paperless):
        """Test controller."""
        assert isinstance(api_23.workflow_actions, WorkflowActionsController)
        # test mixins
        assert hasattr(api_23.workflow_actions, "list")
        assert hasattr(api_23.workflow_actions, "get")
        assert hasattr(api_23.workflow_actions, "iterate")
        assert hasattr(api_23.workflow_actions, "one")
        assert not hasattr(api_23.workflow_actions, "create")
        assert not hasattr(api_23.workflow_actions, "update")
        assert not hasattr(api_23.workflow_actions, "delete")

    async def test_list(self, api_23: Paperless):
        """Test list."""
        items = await api_23.workflow_actions.list()
        assert isinstance(items, list)
        assert len(items) > 0
        for item in items:
            assert isinstance(item, int)

    async def test_get(self, api_23: Paperless):
        """Test get."""
        results = await api_23.workflow_actions.get()
        assert isinstance(results, ResultPage)
        assert results.current_page == 1
        assert not results.next_page  # there is 1 page in sample data
        assert results.last_page == 1  # there is 1 page in sample data
        assert isinstance(results.items, list)
        for item in results.items:
            assert isinstance(item, WorkflowAction)

    async def test_iterate(self, api_23: Paperless):
        """Test iterate."""
        async for item in api_23.workflow_actions.iterate():
            assert isinstance(item, WorkflowAction)

    async def test_one(self, api_23: Paperless):
        """Test one."""
        item = await api_23.workflow_actions.one(1)
        assert item
        assert isinstance(item, WorkflowAction)
        # must raise as 1337 doesn't exist
        with pytest.raises(HTTPNotFound):
            await api_23.workflow_actions.one(1337)


class TestWorkflowTriggers:
    """Workflow Triggers test cases."""

    async def test_controller(self, api_23: Paperless):
        """Test controller."""
        assert isinstance(api_23.workflow_triggers, WorkflowTriggersController)
        # test mixins
        assert hasattr(api_23.workflow_triggers, "list")
        assert hasattr(api_23.workflow_triggers, "get")
        assert hasattr(api_23.workflow_triggers, "iterate")
        assert hasattr(api_23.workflow_triggers, "one")
        assert not hasattr(api_23.workflow_triggers, "create")
        assert not hasattr(api_23.workflow_triggers, "update")
        assert not hasattr(api_23.workflow_triggers, "delete")

    async def test_list(self, api_23: Paperless):
        """Test list."""
        items = await api_23.workflow_triggers.list()
        assert isinstance(items, list)
        assert len(items) > 0
        for item in items:
            assert isinstance(item, int)

    async def test_get(self, api_23: Paperless):
        """Test get."""
        results = await api_23.workflow_triggers.get()
        assert isinstance(results, ResultPage)
        assert results.current_page == 1
        assert not results.next_page  # there is 1 page in sample data
        assert results.last_page == 1  # there is 1 page in sample data
        assert isinstance(results.items, list)
        for item in results.items:
            assert isinstance(item, WorkflowTrigger)

    async def test_iterate(self, api_23: Paperless):
        """Test iterate."""
        async for item in api_23.workflow_triggers.iterate():
            assert isinstance(item, WorkflowTrigger)

    async def test_one(self, api_23: Paperless):
        """Test one."""
        item = await api_23.workflow_triggers.one(1)
        assert item
        assert isinstance(item, WorkflowTrigger)
        # must raise as 1337 doesn't exist
        with pytest.raises(HTTPNotFound):
            await api_23.workflow_triggers.one(1337)
