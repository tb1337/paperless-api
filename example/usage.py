"""Example usage."""

import asyncio
import logging

from pypaperless import Paperless

paperless = Paperless(
    "localhost:8000",
    "ultra-secret-api-token",
    request_opts={"ssl": False},
)
paperless.logger.setLevel(logging.DEBUG)
paperless.logger.addHandler(logging.StreamHandler())


async def main():
    """Execute main function."""
    async with paperless as p:
        correspondents = {}
        async for item in p.correspondents.iterate():
            correspondents[item.id] = item

        documents = await p.documents.get(page=1)
        for item in documents.items:
            print(f"Correspondent of document {item.id} is: {correspondents[item.correspondent]}!")
            await asyncio.sleep(0.05)


if __name__ == "__main__":
    asyncio.run(main())
