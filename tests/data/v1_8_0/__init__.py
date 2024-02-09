"""Raw data constants for Paperless versions >= 1.8.0."""

from tests.const import PAPERLESS_TEST_URL

V1_8_0_PATHS = {
    "storage_paths": f"{PAPERLESS_TEST_URL}/api/storage_paths/",
}

V1_8_0_STORAGE_PATHS = {
    "count": 3,
    "next": None,
    "previous": None,
    "all": [1, 2, 3, 4, 5],
    "results": [
        {
            "id": 1,
            "slug": "work",
            "name": "Work Work Work",
            "path": "{owner_username}/work/{correspondent}_{created}_{document_type}_{title}",
            "match": "",
            "matching_algorithm": 6,
            "is_insensitive": True,
            "document_count": 384,
            "owner": 3,
            "user_can_change": True,
        },
        {
            "id": 2,
            "slug": "banking",
            "name": "Banking",
            "path": "{owner_username}/banking/{correspondent}_{created}_{document_type}_{title}",
            "match": "",
            "matching_algorithm": 6,
            "is_insensitive": True,
            "document_count": 303,
            "owner": None,
            "user_can_change": True,
        },
        {
            "id": 3,
            "slug": "another-test",
            "name": "Another Test",
            "path": "Test/Path/{doc_pk}",
            "match": "",
            "matching_algorithm": 0,
            "is_insensitive": True,
            "document_count": 0,
            "owner": None,
            "user_can_change": True,
        },
        {
            "id": 4,
            "slug": "another-test-2",
            "name": "Another Test 2",
            "path": "Test/Path/{doc_pk}",
            "match": "",
            "matching_algorithm": 0,
            "is_insensitive": True,
            "document_count": 0,
            "owner": None,
            "user_can_change": True,
        },
        {
            "id": 5,
            "slug": "another-test-3",
            "name": "Another Test 3",
            "path": "Test/Path/{doc_pk}",
            "match": "",
            "matching_algorithm": 0,
            "is_insensitive": True,
            "document_count": 0,
            "owner": None,
            "user_can_change": True,
        },
    ],
}
