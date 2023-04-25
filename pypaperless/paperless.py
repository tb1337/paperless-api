from typing import List
from datetime import datetime

from .auth import Auth
from .model import *

from aiohttp import FormData, ClientSession


class PaperlessAPI:
    """Class to communicate with the paginated API."""

    def __init__(self, endpoint: str, token: str = None, username: str = None, password: str = None):
        """Initialize the API and store the auth so we can make token-based or Basic-auth requests."""
        self.auth = Auth(endpoint=endpoint,token=token,username=username, password=password)

    async def __get_paginated_results(self, path: str, isa: object, params = None) -> List[object]:
        """Walk through the pagination and return a list of objects of type <isa>."""
        json = {}
        results = []

        async with ClientSession() as session:
            while True:
                if not "next" in json:
                    resp = await self.auth.request(session, "get", path, params=params)
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
    
    async def __get_non_paginated_results(self, path: str, isa: object, params = None) -> List[object]:
        """Walk through the pagination and return a list of objects of type <isa>."""
        json = {}
        results = []

        async with ClientSession() as session:
            resp = await self.auth.request(session, "get", path, params=params)
            resp.raise_for_status()
            
            json = await resp.json()

            # extend list
            results.extend([isa(data, self.auth)
                            for data in json])
        return results
    
    async def __get_result(self, path: str, isa: object, params = None) -> object:
        """ Return an objects of type <isa>."""
        json = {}

        async with ClientSession() as session:
            resp = await self.auth.request(session, "get", path, params=params)
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
        """Return single document by id."""
        return await self.__get_result(f"documents/{id}", Document)

    async def get_documents(self) -> List[Document]:
        """Return all documents."""
        return await self.__get_paginated_results("documents", Document)

    async def get_task(self, id: int) -> Task:
        """Return single task by id."""
        return await self.__get_result(f"tasks/{id}", Task)

    async def get_task_by_task_id(self, task_id: str) -> Task:
        """Return single task by task id."""
        params = {}
        params["task_id"] = task_id
        # Paperless REST API returns an array with one element and not a single object
        result = await self.__get_non_paginated_results(f"tasks", Task, params=params)
        if len(result) == 1:
            return result[0]
        else:
            return None

    async def get_tasks(self) -> List[Task]:
        """Return all tasks."""
        return await self.__get_non_paginated_results("tasks", Task)
        
    async def post_document(self, file, title: str = "", created: datetime = None, correspondent: int = None, document_type: int = None, tags: List[int] = None) -> object:
        """Post new document and returns task id"""
        async with ClientSession() as session:
            form = FormData()

            form.add_field("document", open(file, 'rb'))

            if title:
                form.add_field("title", title)

            if created:
                form.add_field("created", f"{created}")
            if correspondent:
                form.add_field("correspondent", f"{correspondent}")
            if document_type:
                form.add_field("document_type", f"{document_type}")            
            if tags:
                for tag in tags:
                    form.add_field("tags",f"{tag}")            

            resp = await self.auth.request(session=session, method="post", path="documents/post_document", data=form)
            resp.raise_for_status()
            return await resp.json()
    
    async def search(self, query: str) -> List[Document]:
        params = {}
        params["query"] = query
        return await self.__get_paginated_results("documents", Document, params)