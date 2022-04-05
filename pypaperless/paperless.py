from typing import List

from .auth import Auth
from .model import *

import aiohttp


class PaperlessAPI:
    """Class to communicate with the API."""

    def __init__(self, endpoint: str, token: str, sync_delay: int = 300):
        """Initialize the API and store the auth so we can make requests."""
        self.auth = Auth(endpoint, token)
        self.sync_delay = sync_delay

        self.__correspontents_cache = None
        self.__correspontents_last_sync = None
        self.__document_types_cache = None
        self.__document_types_last_sync = None
        self.__tags_cache = None
        self.__tags_last_sync = None
        self.__saved_views_cache = None
        self.__saved_views_last_sync = None
        self.__documents_cache = None
        self.__documents_last_sync = None

    async def __get_paginated_results(self, path: str, isa: object) -> List[object]:
        """ REturn bla."""
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
        """Return the correspondents."""
        try:
            delta = (datetime.now() -
                     self.__correspontents_last_sync).total_seconds()
        except:
            delta = 0

        if self.__correspontents_last_sync is None or delta > self.sync_delay:
            self.__correspontents_cache = await self.__get_paginated_results(
                "correspondents", Correspondent)
            self.__correspontents_last_sync = datetime.now()

        return self.__correspontents_cache

    async def get_document_types(self) -> List[DocumentType]:
        """Return the correspondents."""
        try:
            delta = (datetime.now() -
                     self.__correspontents_last_sync).total_seconds()
        except:
            delta = 0

        if self.__document_types_last_sync is None or delta > self.sync_delay:
            self.__document_types_cache = await self.__get_paginated_results(
                "document_types", DocumentType)
            self.__document_types_last_sync = datetime.now()

        return self.__document_types_cache

    async def get_tags(self) -> List[Tag]:
        """Return the correspondents."""
        try:
            delta = (datetime.now() -
                     self.__tags_last_sync).total_seconds()
        except:
            delta = 0

        if self.__tags_last_sync is None or delta > self.sync_delay:
            self.__tags_cache = await self.__get_paginated_results("tags", Tag)
            self.__tags_last_sync = datetime.now()

        return self.__tags_cache

    async def get_saved_views(self) -> List[SavedView]:
        """Return the correspondents."""
        try:
            delta = (datetime.now() -
                     self.__saved_views_last_sync).total_seconds()
        except:
            delta = 0

        if self.__saved_views_last_sync is None or delta > self.sync_delay:
            self.__saved_views_cache = await self.__get_paginated_results(
                "saved_views", SavedView)
            self.__saved_views_last_sync = datetime.now()

        return self.__saved_views_cache

    async def get_documents(self) -> List[Document]:
        """Return the correspondents."""
        try:
            delta = (datetime.now() -
                     self.__documents_last_sync).total_seconds()
        except:
            delta = 0

        if self.__documents_last_sync is None or delta > self.sync_delay:
            self.__documents_cache = await self.__get_paginated_results(
                "documents", Document)
            self.__documents_last_sync = datetime.now()

        return self.__documents_cache
