"""Example usage."""

import asyncio
import logging
import os.path
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)-8s %(name)s - %(message)s",
)

from pypaperless import Paperless  # noqa

paperless = Paperless(
    "localhost:8000",
    # replace with your own token
    "17d85e03b83c4bfd9aa0e9a4e71dc3b79265d51e",
    request_opts={"ssl": False},
)


async def main():
    """Execute main function."""
    async with paperless as p:
        correspondents = {}
        async for item in p.correspondents.iterate():
            correspondents[item.id] = item

        documents = await p.documents.get(page=1)
        for item in documents.items:
            print(
                f"Correspondent of document {item.id} is: {correspondents[item.correspondent].name}!"  # noqa
            )
            await asyncio.sleep(0.25)


if __name__ == "__main__":
    asyncio.run(main())
