from typing import List
from datetime import datetime

from .auth import Auth
from .model import *

import aiohttp


class PaperlessAPI:
    """Class to communicate with the paginated API."""

    def __init__(self, endpoint: str, token: str):
        """Initialize the API and store the auth so we can make token-based requests."""
        self.auth = Auth(endpoint, token)

    def __init__(self, endpoint: str, username: str, password: str):
        """Initialize the API and store the auth so we can make token-based requests."""
        self.auth = Auth(endpoint, username, password)

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
    
    async def __get_result(self, path: str, isa: object) -> object:
        """ Return an objects of type <isa>."""
        json = {}

        async with aiohttp.ClientSession() as session:
            resp = await self.auth.request(session, "get", path)
            resp.raise_for_status()

            json = dict(await resp.json())

            return isa(json, self.auth)
    
    async def get_correspondent(self, id: int) -> Correspondent:
        """Return single correspondent by id."""
        return await self.__get_result(f"correspondents/{id}", Correspondent)

    async def get_correspondents(self) -> List[Correspondent]:
        """Return all correspondents."""
        return await self.__get_paginated_results("correspondents", Correspondent)

    async def get_document_type(self, id: int) -> DocumentType:
        """Return single document type by id."""
        return await self.__get_result(f"document_type/{id}", DocumentType)

    async def get_document_types(self) -> List[DocumentType]:
        """Return all document types."""
        return await self.__get_paginated_results("document_types", DocumentType)

    async def get_tag(self, id: int) -> Tag:
        """Return single tag by id."""
        return await self.__get_result(f"tags/{id}", Tag)
    
    async def get_tags(self) -> List[Tag]:
        """Return all tags."""
        return await self.__get_paginated_results("tags", Tag)
    
    async def get_saved_views(self) -> List[SavedView]:
        """Return all saved views."""
        return await self.__get_paginated_results("saved_views", SavedView)

    async def get_document(self, id: int) -> Document:
        return await self.__get_result(f"documents/{id}", Document)

    async def get_documents(self) -> List[Document]:
        """Return all documents."""
        return await self.__get_paginated_results("documents", Document)
    
    async def post_document(self, file, title: str = "", created: datetime = None, correspondent: int = None, document_type: int = None):
        """Post new document."""
        async with aiohttp.ClientSession() as session:
            data = {
                "document": open(file, 'rb'),
                "title": f"{title}",
            }
            if created:
                data["created"] = f"{created}"
            if correspondent:
                data["correspondent"] = f"{correspondent}"
            if document_type:
                data["document_type"] = f"{document_type}"

            resp = await self.auth.request(session=session, method="post", path="documents/post_document/", data=data)
            resp.raise_for_status()
