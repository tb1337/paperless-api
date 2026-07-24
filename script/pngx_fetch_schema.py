"""Fetch the OpenAPI schema from the dev Paperless-ngx instance and write it to tests/data/schema.json."""

# ruff: noqa
# mypy: ignore-errors

import json
import pathlib
import sys

import httpx

from _dev_env import load_dev_env

_env = load_dev_env()
SCHEMA_URL = f"{_env.url}/api/schema/?format=json"
PAPERLESS_TOKEN = _env.token.get_secret_value()
OUTPUT_PATH = pathlib.Path(__file__).parent.parent / "tests" / "data" / "schema.json"


def main() -> None:
    print(f"Fetching {SCHEMA_URL} …")
    response = httpx.get(
        SCHEMA_URL,
        headers={"accept": "application/json", "authorization": f"Token {PAPERLESS_TOKEN}"},
        follow_redirects=True,
        timeout=30,
    )
    response.raise_for_status()

    schema = response.json()
    OUTPUT_PATH.write_text(
        json.dumps(schema, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    print(f"Written to {OUTPUT_PATH}  ({OUTPUT_PATH.stat().st_size:,} bytes)")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
