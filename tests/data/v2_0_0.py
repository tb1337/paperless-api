"""Raw data constants for Paperless versions >= 2.0.0."""

from tests.const import PAPERLESS_TEST_URL

V2_0_0_PATHS = {
    "config": f"{PAPERLESS_TEST_URL}/api/config/",
    "custom_fields": f"{PAPERLESS_TEST_URL}/api/custom_fields/",
    "share_links": f"{PAPERLESS_TEST_URL}/api/share_links/",
}

V2_0_0_CONFIG = [
    {
        "id": 1,
        "user_args": None,
        "output_type": "pdf",
        "pages": None,
        "language": "eng",
        "mode": None,
        "skip_archive_file": None,
        "image_dpi": None,
        "unpaper_clean": None,
        "deskew": None,
        "rotate_pages": None,
        "rotate_pages_threshold": None,
        "max_image_pixels": None,
        "color_conversion_strategy": None,
        "app_title": None,
        "app_logo": None,
    }
]

V2_0_0_CUSTOM_FIELDS = {
    "count": 8,
    "next": None,
    "previous": None,
    "all": [8, 7, 6, 5, 4, 3, 2, 1],
    "results": [
        {"id": 8, "name": "Custom Link", "data_type": "documentlink"},
        {"id": 7, "name": "Custom URL", "data_type": "url"},
        {"id": 6, "name": "Custom Text -added-", "data_type": "string"},
        {"id": 5, "name": "Custom MONEYY $$$", "data_type": "monetary"},
        {"id": 4, "name": "Custom Floating", "data_type": "float"},
        {"id": 3, "name": "Custom Int", "data_type": "integer"},
        {"id": 2, "name": "Custom Date", "data_type": "date"},
        {"id": 1, "name": "Custom Bool", "data_type": "boolean"},
    ],
}

V2_0_0_SHARE_LINKS = {
    "count": 5,
    "next": None,
    "previous": None,
    "all": [1, 2, 3, 4, 5, 6, 7, 8],
    "results": [
        {
            "id": 1,
            "created": "2023-12-11T14:06:49.096456+00:00",
            "expiration": "2023-12-18T14:06:49.064000+00:00",
            "slug": "GMIFR9WVPe7a0FAltmrAdmVsrrTzH6Z9yFi2jufhi5yCTAMWfF",
            "document": 1,
            "file_version": "original",
        },
        {
            "id": 2,
            "created": "2023-12-11T14:06:53.583496+00:00",
            "expiration": "2024-01-10T14:06:53.558000+00:00",
            "slug": "Px2h3mrkIvExyTE8M8usrTLv3jtTb4MnLJ4eTAxcjy2FUmuDLq",
            "document": 2,
            "file_version": "original",
        },
        {
            "id": 3,
            "created": "2023-12-11T14:06:55.984583+00:00",
            "expiration": None,
            "slug": "bDnxeQ4UmlFVUYCDrb1KBLbE4HVSW8jw3CLElcwPyAncV5eiI+00:00",
            "document": 1,
            "file_version": "original",
        },
        {
            "id": 4,
            "created": "2023-12-11T14:07:01.448813+00:00",
            "expiration": "2023-12-12T14:07:01.423000+00:00",
            "slug": "HfzHhDzA03ZQg4t4TAlOuup59qgQA18Zjbb9eOE06PZ8KTjgOb",
            "document": 2,
            "file_version": "archive",
        },
        {
            "id": 5,
            "created": "2023-12-11T14:11:50.710369+00:00",
            "expiration": None,
            "slug": "7PIGEZbeFv5yIrnpSVwj1QeXiJu0IZCiEWGIV4aUHQrfUQtXne",
            "document": 1,
            "file_version": "archive",
        },
        {
            "id": 6,
            "created": "2023-12-11T14:11:50.710369+00:00",
            "expiration": None,
            "slug": "7PIGEZbeFv5yIrnpSVwj1QeXiJu0IZCiEWGIV4aUHQrfUQtXne",
            "document": 1,
            "file_version": "archive",
        },
        {
            "id": 7,
            "created": "2023-12-11T14:11:50.710369+00:00",
            "expiration": None,
            "slug": "7PIGEZbeFv5yIrnpSVwj1QeXiJu0IZCiEWGIV4aUHQrfUQtXne",
            "document": 1,
            "file_version": "archive",
        },
        {
            "id": 8,
            "created": "2023-12-11T14:11:50.710369+00:00",
            "expiration": None,
            "slug": "7PIGEZbeFv5yIrnpSVwj1QeXiJu0IZCiEWGIV4aUHQrfUQtXne",
            "document": 1,
            "file_version": "archive",
        },
    ],
}
