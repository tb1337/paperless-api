"""Paperless basic tests."""

import datetime
from unittest.mock import patch

import pytest
from aiohttp.web_exceptions import HTTPNotFound

from pypaperless import Paperless
from pypaperless.controllers import (
    CorrespondentsController,
    DocumentsController,
    DocumentTypesController,
    GroupsController,
    MailAccountsController,
    MailRulesController,
    SavedViewsController,
    TagsController,
    TasksController,
    UsersController,
)
from pypaperless.controllers.base import ResultPage
from pypaperless.models import (
    Correspondent,
    CorrespondentPost,
    Document,
    DocumentMetadata,
    DocumentMetaInformation,
    DocumentPost,
    DocumentType,
    DocumentTypePost,
    Group,
    MailAccount,
    MailRule,
    SavedView,
    Tag,
    TagPost,
    Task,
    User,
)
from pypaperless.models.matching import MatchingAlgorithm


class TestBeginPaperless:
    """Common Paperless test cases."""

    async def test_init(self, api_00: Paperless):
        """Test init."""
        assert api_00._token
        assert api_00._request_opts
        assert not api_00._session
        # test properties
        assert api_00.url
        assert api_00.is_initialized

    async def test_features(self, api_00: Paperless):
        """Test features."""
        # basic class has no features
        assert api_00.features == 0
        assert not api_00.storage_paths
        assert not api_00.consumption_templates
        assert not api_00.custom_fields
        assert not api_00.share_links
        assert not api_00.workflows
        assert not api_00.workflow_actions
        assert not api_00.workflow_triggers

    async def test_enums(self):
        """Test enums."""
        assert MatchingAlgorithm(999) == MatchingAlgorithm.UNKNOWN


class TestCorrespondents:
    """Correspondents test cases."""

    async def test_controller(self, api_00: Paperless):
        """Test controller."""
        assert isinstance(api_00.correspondents, CorrespondentsController)
        # test mixins
        assert hasattr(api_00.correspondents, "list")
        assert hasattr(api_00.correspondents, "get")
        assert hasattr(api_00.correspondents, "iterate")
        assert hasattr(api_00.correspondents, "one")
        assert hasattr(api_00.correspondents, "create")
        assert hasattr(api_00.correspondents, "update")
        assert hasattr(api_00.correspondents, "delete")

    async def test_list(self, api_00: Paperless):
        """Test list."""
        items = await api_00.correspondents.list()
        assert isinstance(items, list)
        assert len(items) > 0
        for item in items:
            assert isinstance(item, int)

    async def test_get(self, api_00: Paperless):
        """Test get."""
        results = await api_00.correspondents.get()
        assert isinstance(results, ResultPage)
        assert results.current_page == 1
        assert not results.next_page  # there is 1 page in sample data
        assert results.last_page == 1  # there is 1 page in sample data
        assert isinstance(results.items, list)
        for item in results.items:
            assert isinstance(item, Correspondent)

    async def test_iterate(self, api_00: Paperless):
        """Test iterate."""
        async for item in api_00.correspondents.iterate():
            assert isinstance(item, Correspondent)

    async def test_one(self, api_00: Paperless):
        """Test one."""
        item = await api_00.correspondents.one(1)
        assert item
        assert isinstance(item, Correspondent)
        # must raise as 1337 doesn't exist
        with pytest.raises(HTTPNotFound):
            await api_00.correspondents.one(1337)

    async def test_create(self, api_00: Paperless):
        """Test create."""
        new_name = "Created Correspondent"
        to_create = CorrespondentPost(name=new_name)
        # test mixins, and their defaults
        assert to_create.is_insensitive is True
        assert to_create.match == ""
        assert to_create.matching_algorithm == MatchingAlgorithm.NONE
        # test default override
        to_create = CorrespondentPost(
            name=new_name,
            matching_algorithm=MatchingAlgorithm.FUZZY,
        )
        assert to_create.matching_algorithm == MatchingAlgorithm.FUZZY
        # actually call the create endpoint
        created = await api_00.correspondents.create(to_create)
        assert isinstance(created, Correspondent)
        assert created.id == 6
        assert created.matching_algorithm == MatchingAlgorithm.FUZZY

    async def test_udpate(self, api_00: Paperless):
        """Test update."""
        new_name = "Created Correspondent Update"
        to_update = await api_00.correspondents.one(6)
        to_update.name = new_name
        updated = await api_00.correspondents.update(to_update)
        assert isinstance(updated, Correspondent)
        assert updated.name == new_name

    async def test_delete(self, api_00: Paperless):
        """Test delete."""
        to_delete = await api_00.correspondents.one(6)
        deleted = await api_00.correspondents.delete(to_delete)
        assert deleted
        # must raise as we deleted 6
        with pytest.raises(HTTPNotFound):
            await api_00.correspondents.one(6)


class TestDocuments:
    """Documents test cases."""

    async def test_controller(self, api_00: Paperless):
        """Test controller."""
        assert isinstance(api_00.documents, DocumentsController)
        # test mixins
        assert hasattr(api_00.documents, "list")
        assert hasattr(api_00.documents, "get")
        assert hasattr(api_00.documents, "iterate")
        assert hasattr(api_00.documents, "one")
        assert hasattr(api_00.documents, "create")
        assert hasattr(api_00.documents, "update")
        assert hasattr(api_00.documents, "delete")
        # test services
        assert api_00.documents.files
        assert not api_00.documents.notes

    async def test_list(self, api_00: Paperless):
        """Test list."""
        items = await api_00.documents.list()
        assert isinstance(items, list)
        assert len(items) > 0
        for item in items:
            assert isinstance(item, int)

    async def test_empty_list(self, api_00: Paperless):
        """Test empty controller list."""
        with patch.object(api_00, "request_json", return_value={}):
            # list must be empty because "all" key is omitted in return value
            items = await api_00.documents.list()
            assert items == []

    async def test_get(self, api_00: Paperless):
        """Test get."""
        results = await api_00.documents.get()
        assert isinstance(results, ResultPage)
        assert results.current_page == 1
        assert not results.next_page  # there is 1 page in sample data
        assert results.last_page == 1  # there is 1 page in sample data
        assert isinstance(results.items, list)
        for item in results.items:
            assert isinstance(item, Document)

    async def test_iterate(self, api_00: Paperless):
        """Test iterate."""
        async for item in api_00.documents.iterate():
            assert isinstance(item, Document)

    async def test_one(self, api_00: Paperless):
        """Test one."""
        item = await api_00.documents.one(1)
        assert item
        assert isinstance(item, Document)
        # must raise as 1337 doesn't exist
        with pytest.raises(HTTPNotFound):
            await api_00.documents.one(1337)

    async def test_create(self, api_00: Paperless):
        """Test create."""
        new_document = b"example content"
        new_tags = [1, 2, 3]
        new_correspondent = 1
        new_document_type = 1
        new_storage_path = 1
        title = "New Document"
        created = datetime.datetime.now()
        new_asn = 1
        to_create = DocumentPost(
            document=new_document,
            tags=new_tags,
            title=title,
            correspondent=new_correspondent,
            document_type=new_document_type,
            storage_path=new_storage_path,
            created=created,
            archive_serial_number=new_asn,
        )
        # actually call the create endpoint
        task_id = await api_00.documents.create(to_create)
        assert isinstance(task_id, str)
        task = await api_00.tasks.one(task_id)
        assert task.related_document
        created = await api_00.documents.one(task.related_document)
        assert isinstance(created, Document)
        assert created.tags.count(1) == 1
        assert created.tags.count(2) == 1
        assert created.tags.count(3) == 1

    async def test_udpate(self, api_00: Paperless):
        """Test update."""
        new_name = "Created Document Update"
        to_update = await api_00.documents.one(3)
        to_update.title = new_name
        updated = await api_00.documents.update(to_update)
        assert isinstance(updated, Document)
        assert updated.title == new_name

    async def test_delete(self, api_00: Paperless):
        """Test delete."""
        to_delete = await api_00.documents.one(3)
        deleted = await api_00.documents.delete(to_delete)
        assert deleted
        # must raise as we deleted 6
        with pytest.raises(HTTPNotFound):
            await api_00.documents.one(6)

    async def test_meta(self, api_00: Paperless):
        """Test meta."""
        # test with pk
        meta = await api_00.documents.meta(1)
        assert isinstance(meta, DocumentMetaInformation)
        # test with item
        item = await api_00.documents.one(1)
        meta = await api_00.documents.meta(item)
        assert isinstance(meta.original_metadata, list)
        for item in meta.original_metadata:
            assert isinstance(item, DocumentMetadata)
        assert isinstance(meta.archive_metadata, list)
        for item in meta.archive_metadata:
            assert isinstance(item, DocumentMetadata)

    async def test_files(self, api_00: Paperless):
        """Test files."""
        # test with pk
        files = await api_00.documents.files.thumb(1)
        assert isinstance(files, bytes)
        files = await api_00.documents.files.preview(1)
        assert isinstance(files, bytes)
        files = await api_00.documents.files.download(1)
        assert isinstance(files, bytes)
        # test with item
        item = await api_00.documents.one(1)
        files = await api_00.documents.files.thumb(item)
        assert isinstance(files, bytes)
        files = await api_00.documents.files.preview(item)
        assert isinstance(files, bytes)
        files = await api_00.documents.files.download(item)
        assert isinstance(files, bytes)


class TestDocumentTypes:
    """Document Types test cases."""

    async def test_controller(self, api_00: Paperless):
        """Test controller."""
        assert isinstance(api_00.document_types, DocumentTypesController)
        # test mixins
        assert hasattr(api_00.document_types, "list")
        assert hasattr(api_00.document_types, "get")
        assert hasattr(api_00.document_types, "iterate")
        assert hasattr(api_00.document_types, "one")
        assert hasattr(api_00.document_types, "create")
        assert hasattr(api_00.document_types, "update")
        assert hasattr(api_00.document_types, "delete")

    async def test_list(self, api_00: Paperless):
        """Test list."""
        items = await api_00.document_types.list()
        assert isinstance(items, list)
        assert len(items) > 0
        for item in items:
            assert isinstance(item, int)

    async def test_get(self, api_00: Paperless):
        """Test get."""
        results = await api_00.document_types.get()
        assert isinstance(results, ResultPage)
        assert results.current_page == 1
        assert not results.next_page  # there is 1 page in sample data
        assert results.last_page == 1  # there is 1 page in sample data
        assert isinstance(results.items, list)
        for item in results.items:
            assert isinstance(item, DocumentType)

    async def test_iterate(self, api_00: Paperless):
        """Test iterate."""
        async for item in api_00.document_types.iterate():
            assert isinstance(item, DocumentType)

    async def test_one(self, api_00: Paperless):
        """Test one."""
        item = await api_00.document_types.one(1)
        assert item
        assert isinstance(item, DocumentType)
        # must raise as 1337 doesn't exist
        with pytest.raises(HTTPNotFound):
            await api_00.document_types.one(1337)

    async def test_create(self, api_00: Paperless):
        """Test create."""
        new_name = "Created Document Type"
        to_create = DocumentTypePost(name=new_name)
        # test mixins, and their defaults
        assert to_create.is_insensitive is True
        assert to_create.match == ""
        assert to_create.matching_algorithm == MatchingAlgorithm.NONE
        # test default override
        to_create = DocumentTypePost(
            name=new_name,
            matching_algorithm=MatchingAlgorithm.FUZZY,
        )
        assert to_create.matching_algorithm == MatchingAlgorithm.FUZZY
        # actually call the create endpoint
        created = await api_00.document_types.create(to_create)
        assert isinstance(created, DocumentType)
        assert created.id == 6
        assert created.matching_algorithm == MatchingAlgorithm.FUZZY

    async def test_udpate(self, api_00: Paperless):
        """Test update."""
        new_name = "Created Document Type Update"
        to_update = await api_00.document_types.one(6)
        to_update.name = new_name
        updated = await api_00.document_types.update(to_update)
        assert isinstance(updated, DocumentType)
        assert updated.name == new_name

    async def test_delete(self, api_00: Paperless):
        """Test delete."""
        to_delete = await api_00.document_types.one(6)
        deleted = await api_00.document_types.delete(to_delete)
        assert deleted
        # must raise as we deleted 6
        with pytest.raises(HTTPNotFound):
            await api_00.document_types.one(6)


class TestGroups:
    """Groups test cases."""

    async def test_controller(self, api_00: Paperless):
        """Test controller."""
        assert isinstance(api_00.groups, GroupsController)
        # test mixins
        assert hasattr(api_00.groups, "list")
        assert hasattr(api_00.groups, "get")
        assert hasattr(api_00.groups, "iterate")
        assert hasattr(api_00.groups, "one")
        assert not hasattr(api_00.groups, "create")
        assert not hasattr(api_00.groups, "update")
        assert not hasattr(api_00.groups, "delete")

    async def test_list(self, api_00: Paperless):
        """Test list."""
        items = await api_00.groups.list()
        assert isinstance(items, list)
        assert len(items) > 0
        for item in items:
            assert isinstance(item, int)

    async def test_get(self, api_00: Paperless):
        """Test get."""
        results = await api_00.groups.get()
        assert isinstance(results, ResultPage)
        assert results.current_page == 1
        assert not results.next_page  # there is 1 page in sample data
        assert results.last_page == 1  # there is 1 page in sample data
        assert isinstance(results.items, list)
        for item in results.items:
            assert isinstance(item, Group)

    async def test_iterate(self, api_00: Paperless):
        """Test iterate."""
        async for item in api_00.groups.iterate():
            assert isinstance(item, Group)

    async def test_one(self, api_00: Paperless):
        """Test one."""
        item = await api_00.groups.one(1)
        assert item
        assert isinstance(item, Group)
        # must raise as 1337 doesn't exist
        with pytest.raises(HTTPNotFound):
            await api_00.groups.one(1337)


class TestMailAccounts:
    """Mail Accounts test cases."""

    async def test_controller(self, api_00: Paperless):
        """Test controller."""
        assert isinstance(api_00.mail_accounts, MailAccountsController)
        # test mixins
        assert hasattr(api_00.mail_accounts, "list")
        assert hasattr(api_00.mail_accounts, "get")
        assert hasattr(api_00.mail_accounts, "iterate")
        assert hasattr(api_00.mail_accounts, "one")
        assert not hasattr(api_00.mail_accounts, "create")
        assert not hasattr(api_00.mail_accounts, "update")
        assert not hasattr(api_00.mail_accounts, "delete")

    async def test_list(self, api_00: Paperless):
        """Test list."""
        items = await api_00.mail_accounts.list()
        assert isinstance(items, list)
        assert len(items) > 0
        for item in items:
            assert isinstance(item, int)

    async def test_get(self, api_00: Paperless):
        """Test get."""
        results = await api_00.mail_accounts.get()
        assert isinstance(results, ResultPage)
        assert results.current_page == 1
        assert not results.next_page  # there is 1 page in sample data
        assert results.last_page == 1  # there is 1 page in sample data
        assert isinstance(results.items, list)
        for item in results.items:
            assert isinstance(item, MailAccount)

    async def test_iterate(self, api_00: Paperless):
        """Test iterate."""
        async for item in api_00.mail_accounts.iterate():
            assert isinstance(item, MailAccount)

    async def test_one(self, api_00: Paperless):
        """Test one."""
        item = await api_00.mail_accounts.one(1)
        assert item
        assert isinstance(item, MailAccount)
        # must raise as 1337 doesn't exist
        with pytest.raises(HTTPNotFound):
            await api_00.mail_accounts.one(1337)


class TestMailRules:
    """Mail Rules test cases."""

    async def test_controller(self, api_00: Paperless):
        """Test controller."""
        assert isinstance(api_00.mail_rules, MailRulesController)
        # test mixins
        assert hasattr(api_00.mail_rules, "list")
        assert hasattr(api_00.mail_rules, "get")
        assert hasattr(api_00.mail_rules, "iterate")
        assert hasattr(api_00.mail_rules, "one")
        assert not hasattr(api_00.mail_rules, "create")
        assert not hasattr(api_00.mail_rules, "update")
        assert not hasattr(api_00.mail_rules, "delete")

    async def test_list(self, api_00: Paperless):
        """Test list."""
        items = await api_00.mail_rules.list()
        assert isinstance(items, list)
        assert len(items) > 0
        for item in items:
            assert isinstance(item, int)

    async def test_get(self, api_00: Paperless):
        """Test get."""
        results = await api_00.mail_rules.get()
        assert isinstance(results, ResultPage)
        assert results.current_page == 1
        assert not results.next_page  # there is 1 page in sample data
        assert results.last_page == 1  # there is 1 page in sample data
        assert isinstance(results.items, list)
        for item in results.items:
            assert isinstance(item, MailRule)

    async def test_iterate(self, api_00: Paperless):
        """Test iterate."""
        async for item in api_00.mail_rules.iterate():
            assert isinstance(item, MailRule)

    async def test_one(self, api_00: Paperless):
        """Test one."""
        item = await api_00.mail_rules.one(1)
        assert item
        assert isinstance(item, MailRule)
        # must raise as 1337 doesn't exist
        with pytest.raises(HTTPNotFound):
            await api_00.mail_rules.one(1337)


class TestSavedViews:
    """Saved Views test cases."""

    async def test_controller(self, api_00: Paperless):
        """Test controller."""
        assert isinstance(api_00.saved_views, SavedViewsController)
        # test mixins
        assert hasattr(api_00.saved_views, "list")
        assert hasattr(api_00.saved_views, "get")
        assert hasattr(api_00.saved_views, "iterate")
        assert hasattr(api_00.saved_views, "one")
        assert not hasattr(api_00.saved_views, "create")
        assert not hasattr(api_00.saved_views, "update")
        assert not hasattr(api_00.saved_views, "delete")

    async def test_list(self, api_00: Paperless):
        """Test list."""
        items = await api_00.saved_views.list()
        assert isinstance(items, list)
        assert len(items) > 0
        for item in items:
            assert isinstance(item, int)

    async def test__get(self, api_00: Paperless):
        """Test get."""
        results = await api_00.saved_views.get()
        assert isinstance(results, ResultPage)
        assert results.current_page == 1
        assert not results.next_page  # there is 1 page in sample data
        assert results.last_page == 1  # there is 1 page in sample data
        assert isinstance(results.items, list)
        for item in results.items:
            assert isinstance(item, SavedView)

    async def test_iterate(self, api_00: Paperless):
        """Test iterate."""
        async for item in api_00.saved_views.iterate():
            assert isinstance(item, SavedView)

    async def test_one(self, api_00: Paperless):
        """Test one."""
        item = await api_00.saved_views.one(1)
        assert item
        assert isinstance(item, SavedView)
        # must raise as 1337 doesn't exist
        with pytest.raises(HTTPNotFound):
            await api_00.saved_views.one(1337)


class TestTags:
    """Tags test cases."""

    async def test_controller(self, api_00: Paperless):
        """Test controller."""
        assert isinstance(api_00.tags, TagsController)
        # test mixins
        assert hasattr(api_00.tags, "list")
        assert hasattr(api_00.tags, "get")
        assert hasattr(api_00.tags, "iterate")
        assert hasattr(api_00.tags, "one")
        assert hasattr(api_00.tags, "create")
        assert hasattr(api_00.tags, "update")
        assert hasattr(api_00.tags, "delete")

    async def test_list(self, api_00: Paperless):
        """Test list."""
        items = await api_00.tags.list()
        assert isinstance(items, list)
        assert len(items) > 0
        for item in items:
            assert isinstance(item, int)

    async def test_get(self, api_00: Paperless):
        """Test get."""
        results = await api_00.tags.get()
        assert isinstance(results, ResultPage)
        assert results.current_page == 1
        assert not results.next_page  # there is 1 page in sample data
        assert results.last_page == 1  # there is 1 page in sample data
        assert isinstance(results.items, list)
        for item in results.items:
            assert isinstance(item, Tag)

    async def test_iterate(self, api_00: Paperless):
        """Test iterate."""
        async for item in api_00.tags.iterate():
            assert isinstance(item, Tag)

    async def test_one(self, api_00: Paperless):
        """Test one."""
        item = await api_00.tags.one(1)
        assert item
        assert isinstance(item, Tag)
        # must raise as 1337 doesn't exist
        with pytest.raises(HTTPNotFound):
            await api_00.tags.one(1337)

    async def test_create(self, api_00: Paperless):
        """Test create."""
        new_name = "Created Tag"
        to_create = TagPost(name=new_name)
        # test mixins, and their defaults
        assert to_create.is_insensitive is True
        assert to_create.match == ""
        assert to_create.matching_algorithm == MatchingAlgorithm.NONE
        # test default override
        to_create = TagPost(
            name=new_name,
            matching_algorithm=MatchingAlgorithm.FUZZY,
        )
        assert to_create.matching_algorithm == MatchingAlgorithm.FUZZY
        # actually call the create endpoint
        created = await api_00.tags.create(to_create)
        assert isinstance(created, Tag)
        assert created.id == 3
        assert created.matching_algorithm == MatchingAlgorithm.FUZZY

    async def test_udpate(self, api_00: Paperless):
        """Test update."""
        new_name = "Created Tag Update"
        to_update = await api_00.tags.one(3)
        to_update.name = new_name
        updated = await api_00.tags.update(to_update)
        assert isinstance(updated, Tag)
        assert updated.name == new_name

    async def test_delete(self, api_00: Paperless):
        """Test delete."""
        to_delete = await api_00.tags.one(3)
        deleted = await api_00.tags.delete(to_delete)
        assert deleted
        # must raise as we deleted 3
        with pytest.raises(HTTPNotFound):
            await api_00.tags.one(3)


class TestTasks:
    """Tasks test cases."""

    async def test_controller(self, api_00: Paperless):
        """Test controller."""
        assert isinstance(api_00.tasks, TasksController)
        # test mixins
        assert not hasattr(api_00.tasks, "list")
        assert hasattr(api_00.tasks, "get")
        assert hasattr(api_00.tasks, "iterate")
        assert hasattr(api_00.tasks, "one")
        assert not hasattr(api_00.tasks, "create")
        assert not hasattr(api_00.tasks, "update")
        assert not hasattr(api_00.tasks, "delete")

    async def test_get(self, api_00: Paperless):
        """Test get."""
        results = await api_00.tasks.get()
        assert isinstance(results, list)
        for item in results:
            assert isinstance(item, Task)

    async def test_iterate(self, api_00: Paperless):
        """Test iterate."""
        async for item in api_00.tasks.iterate():
            assert isinstance(item, Task)

    async def test_one(self, api_00: Paperless):
        """Test one."""
        item = await api_00.tasks.one("eb327ed7-b3c8-4a8c-9aa2-5385e499c74a")
        assert isinstance(item, Task)
        item = await api_00.tasks.one("non-existing-uuid")
        assert not item


class TestUsers:
    """Users test cases."""

    async def test_controller(self, api_00: Paperless):
        """Test controller."""
        assert isinstance(api_00.users, UsersController)
        # test mixins
        assert hasattr(api_00.users, "list")
        assert hasattr(api_00.users, "get")
        assert hasattr(api_00.users, "iterate")
        assert hasattr(api_00.users, "one")
        assert not hasattr(api_00.users, "create")
        assert not hasattr(api_00.users, "update")
        assert not hasattr(api_00.users, "delete")

    async def test_list(self, api_00: Paperless):
        """Test list."""
        items = await api_00.users.list()
        assert isinstance(items, list)
        assert len(items) > 0
        for item in items:
            assert isinstance(item, int)

    async def test_get(self, api_00: Paperless):
        """Test get."""
        results = await api_00.users.get()
        assert isinstance(results, ResultPage)
        assert results.current_page == 1
        assert not results.next_page  # there is 1 page in sample data
        assert results.last_page == 1  # there is 1 page in sample data
        assert isinstance(results.items, list)
        for item in results.items:
            assert isinstance(item, User)

    async def test_iterate(self, api_00: Paperless):
        """Test iterate."""
        async for item in api_00.users.iterate():
            assert isinstance(item, User)

    async def test_one(self, api_00: Paperless):
        """Test one."""
        item = await api_00.users.one(1)
        assert item
        assert isinstance(item, User)
        # must raise as 1337 doesn't exist
        with pytest.raises(HTTPNotFound):
            await api_00.users.one(1337)
