"""Test CRUD for documents."""

from unittest.mock import patch

import pytest
from aiohttp import FormData

from pypaperless import Paperless
from pypaperless.models import DocumentPost


@pytest.fixture(scope="module")
def documents_dataset(data):
    """Represent current data."""
    return data["documents"]


async def test_document_create(paperless: Paperless):
    """Test document create."""
    a_sample_document = bytes("Example content.", "utf-8")
    a_sample_title = "Test Title"
    a_sample_correspondent = 1337
    a_sample_doctype = 42
    a_sample_asn = 23
    a_sample_taglist = [0, 1, 1, 2, 3, 5, 8, 13]

    # we check the form data created
    # the test seems useless but it actually executes the create() method
    # and helped me find a dirty bug, so we love each other. obviously. :D

    to_create = DocumentPost(
        document=a_sample_document,
        title=a_sample_title,
        correspondent=a_sample_correspondent,
        document_type=a_sample_doctype,
        archive_serial_number=a_sample_asn,
        tags=a_sample_taglist,
    )

    async def fake_request_json(*args, **kwargs):
        data = kwargs["data"]  # supplied form data

        assert args[0] == "post"
        assert isinstance(data, FormData)

        form = FormData()
        form.add_fields(
            ("document", a_sample_document),
            ("title", a_sample_title),
            ("correspondent", a_sample_correspondent),
            ("document_type", a_sample_doctype),
            ("archive_serial_number", a_sample_asn),
            *(("tags", f"{tag}") for tag in a_sample_taglist),
        )

        assert (
            form._gen_form_urlencoded()._value  # pylint: disable=protected-access
            == data._gen_form_urlencoded()._value  # pylint: disable=protected-access
        )

        return "bd2de639-5ecd-4bc1-ab3d-106908ef00e1"

    # mock request_json() method
    with patch.object(
        paperless,
        "request_json",
        fake_request_json,
    ):
        task_id = await paperless.documents.create(to_create)

        assert isinstance(task_id, str)
        assert len(task_id) == 36
