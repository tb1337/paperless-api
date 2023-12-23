"""Test CRUD."""

from unittest.mock import patch

import pytest

from pypaperless import Paperless
from pypaperless.models import Correspondent, CorrespondentPost
from pypaperless.models.shared import MatchingAlgorithm
from pypaperless.util import dataclass_from_dict, dataclass_to_dict


@pytest.fixture(scope="module")
def correspondent_dataset(data):
    """Represent current data."""
    return data["correspondents"]


async def test_default_create(paperless: Paperless):
    """Test default create."""
    to_create = CorrespondentPost(name="salty correspondent")

    # test matching model defaults
    assert to_create.is_insensitive is True
    assert to_create.match == ""
    assert to_create.matching_algorithm == MatchingAlgorithm.NONE

    to_create.matching_algorithm = MatchingAlgorithm.FUZZY

    with patch.object(paperless, "request_json", return_value=dataclass_to_dict(to_create)):
        created = await paperless.correspondents.create(to_create)

        assert isinstance(created, Correspondent)
        assert created.matching_algorithm == MatchingAlgorithm.FUZZY


async def test_default_update(paperless: Paperless, correspondent_dataset):
    """Test default update."""
    new_name = "Sample Correspondent Updated"

    to_update = dataclass_from_dict(Correspondent, correspondent_dataset["results"][0])
    assert isinstance(to_update, Correspondent)

    to_update.name = new_name

    with patch.object(paperless, "request_json", return_value=dataclass_to_dict(to_update)):
        updated = await paperless.correspondents.update(to_update)

        assert isinstance(updated, Correspondent)
        assert updated.name == new_name


async def test_default_delete(paperless: Paperless, correspondent_dataset):
    """Test default delete."""
    to_delete = dataclass_from_dict(Correspondent, correspondent_dataset["results"][3])
    assert isinstance(to_delete, Correspondent)

    # figuring out how to test that well.
    with patch.object(paperless, "request_json", return_value=True):
        assert await paperless.correspondents.delete(to_delete)
