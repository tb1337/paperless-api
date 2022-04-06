from typing import List

from .auth import Auth
from .model import *

import aiohttp


class PaperlessAPI:
    """Class to communicate with the paginated API."""

    def __init__(self, endpoint: str, token: str):
        """Initialize the API and store the auth so we can make token-based requests."""
        self.auth = Auth(endpoint, token)

    async def __get_paginated_results(self, path: str, isa: object) -> List[object]:
        """Walk through the pagination and return a list of objects of type <isa>."""
        json = {}
        results = []

        async with aiohttp.ClientSession() as session:
            while True:
                if not "next" in json:
                    resp = await self.auth.request(session, "get", path)
                else:
                    resp = await self.auth.request_raw(session, "get", json["next"])
                resp.raise_for_status()

                json = dict(await resp.json())

                # extend list
                results.extend([isa(data, self.auth)
                                for data in json["results"]])

                # end loop when no next is given
                if json["next"] is None:
                    break

        return results

    async def get_correspondents(self) -> List[Correspondent]:
        """Return all correspondents."""
        return await self.__get_paginated_results("correspondents", Correspondent)

    async def get_document_types(self) -> List[DocumentType]:
        """Return all document types."""
        return await self.__get_paginated_results("document_types", DocumentType)

    async def get_tags(self) -> List[Tag]:
        """Return all tags."""
        return await self.__get_paginated_results("tags", Tag)

    async def get_saved_views(self) -> List[SavedView]:
        """Return all saved views."""
        return await self.__get_paginated_results("saved_views", SavedView)

    async def get_documents(self) -> List[Document]:
        """Return all documents."""
        return await self.__get_paginated_results("documents", Document)
