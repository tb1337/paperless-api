"""Example usage."""

import asyncio
import logging

from pypaperless import Paperless

logging.basicConfig(
    level=logging.WARNING,
    format="%(levelname)-8s %(name)s - %(message)s",
)

paperless = Paperless(
    "http://192.168.33.5:8000",
    # replace with your own token
    "51d914d186d0a17cd0d4bdccac35426d58b6e173",
)


async def main() -> None:
    """Execute main function."""
    async with paperless:
        # breakpoint
        __breakpoint__ = True


if __name__ == "__main__":
    asyncio.run(main())
