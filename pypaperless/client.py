# -*- coding: utf-8 -*-

""" A simple and stupid Python lib for the paperless-ngx Rest API """

from typing import List

from .model import *

import json
import base64
import requests
import urllib3


from datetime import datetime, date
def json_serializer(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    
urllib3.disable_warnings()


class Paperless:
    """
        Example usage:

        from pypaperless import *
        paperless = Paperless("http://ip.of.your.installation:8000", "super-secret-token")

        documents = paperless.get_documents()
    """
    
    def __init__(
        self,
        endpoint: str,
        token: str = None,
        username: str = None,
        password: str = None,
        **kwargs
    ):
        """
        Create Paperless client.
        """
        self.basepath = f"{endpoint}/api"
        self.token = token
        self.username = username
        self.password = password
        self.request_opts = dict(kwargs)

        self._session = requests.Session()

    def __del__(self):
        if isinstance(self._session, requests.Session):
            self._session.close()

    def _auth_headers(self):
        if self.token:
            return {"Authorization": f"Token {self.token}"}
        elif self.username and self.password:
            return {"Authorization": 
                "Basic " + 
                    base64.b64encode(
                        f"{self.username}:{self.password}".encode()
                    ).decode()
            }
        else:
            raise RuntimeError("No credentials provided")

    def _request(self, method, url, payload, params):
        args = dict(params=params)
        args.update(self.request_opts)

        headers = self._auth_headers()

        # Use API Version 2 per default
        headers["Accept"] = "application/json; version=2"

        if "content_type" in args["params"]:
            headers["Content-Type"] = args["params"]["content_type"]
            del args["params"]["content_type"]
            if payload:
                args["data"] = payload
        else:
            headers["Content-Type"] = "application/json"
            if payload:
                args["data"] = json.dumps(payload, default=json_serializer)

        try:
            response = self._session.request(method, url, headers=headers, **args)
            results = response.json()

            if response.status_code == 400:
                raise ValueError(f"400 Client Error: Bad Value for field :: {results}")
            response.raise_for_status()
        finally:
            pass

        return results

    def _http_get(self, url, args=None, payload=None, **kwargs):
        if args:
            kwargs.update(args)
        return self._request("GET", url, payload, kwargs)
    
    def _http_post(self, url, args=None, payload=None, **kwargs):
        if args:
            kwargs.update(args)
        return self._request("POST", url, payload, kwargs)
    
    def _http_put(self, url, args=None, payload=None, **kwargs):
        if args:
            kwargs.update(args)
        return self._request("PUT", url, payload, kwargs)

    def _next(
        self, endpoint
    ) -> List[object]:
        data = []
        response = {}

        while True:
            if not "next" in response:
                response = self._http_get(endpoint, format="json")
            else:
                response = self._http_get(response["next"])

            data.extend(response["results"])

            if not response["next"]:
                break

        return data
    

    def get_all(
        self, cls: PaperlessModel
    ) -> List[PaperlessModel]:
        """
        Return a list of model objects. Requests more than once.
        """
        response = self._next(f"{self.basepath}/{cls._endpoint}/")
        return [cls(**item) for item in response]
    

    def get_ids(
        self, cls: PaperlessModel
    ) -> List[int]:
        """
        Return a list of model ids. Requests only once.
        """
        response = self._http_get(f"{self.basepath}/{cls._endpoint}/", format="json")
        return response["all"]
    

    def get(
        self, cls: PaperlessModel, id: int
    ) -> PaperlessModel:
        """
        Return exactly one model by id.
        """
        response = self._http_get(f"{self.basepath}/{cls._endpoint}/{id}/", format="json")
        return cls(**response)

    
    def save(
        self, item: PaperlessModel
    ) -> PaperlessModel:
        """
        Save model object by object.
        """
        if isinstance(item, PaperlessDocumentNote):
            raise TypeError("Updating document notes is currently not supported due to paperless API implementation!")

        response = self._http_put(f"{self.basepath}/{item.__class__._endpoint}/{item.id}/", payload=item.__dict__, format="json")
        return item.__class__(**response)
    

    def create(
        self, item: PaperlessModel
    ) -> PaperlessModel:
        """
        Create new entity by model object.
        """
        if isinstance(item, PaperlessDocument):
            raise TypeError("Use post_document for creating new documents!")
        if isinstance(item, PaperlessDocumentNote):
            raise TypeError("Creating document notes is currently not supported due to paperless API implementation!")

        response = self._http_post(f"{self.basepath}/{item.__class__._endpoint}/", payload=item.__dict__, format="json")
        return item.__class__(**response)
    

    def get_users(self) -> List[PaperlessUser]:
        return self.get_all(PaperlessUser)

    def get_correspondents(self) -> List[PaperlessCorrespondent]:
        return self.get_all(PaperlessCorrespondent)
    
    def get_document_types(self) -> List[PaperlessDocumentType]:
        return self.get_all(PaperlessDocumentType)
    
    def get_tags(self) -> List[PaperlessTag]:
        return self.get_all(PaperlessTag)
    
    def get_saved_views(self) -> List[PaperlessSavedView]:
        return self.get_all(PaperlessSavedView)
    
    def get_documents(self) -> List[PaperlessDocument]:
        return self.get_all(PaperlessDocument)
    
    def get_storage_paths(self) -> List[PaperlessStoragePath]:
        return self.get_all(PaperlessStoragePath)
    
    def get_groups(self) -> List[PaperlessGroup]:
        return self.get_all(PaperlessGroup)
    
    def get_mail_accounts(self) -> List[PaperlessMailAccount]:
        return self.get_all(PaperlessMailAccount)
    
    def get_mail_rules(self) -> List[PaperlessMailRule]:
        return self.get_all(PaperlessMailRule)
    

    def get_user(self, id: int) -> PaperlessUser:
        return self.get(PaperlessUser, id)

    def get_correspondent(self, id: int) -> PaperlessCorrespondent:
        return self.get(PaperlessCorrespondent, id)
    
    def get_document_type(self, id: int) -> PaperlessDocumentType:
        return self.get(PaperlessDocumentType, id)
    
    def get_tag(self, id: int) -> PaperlessTag:
        return self.get(PaperlessTag, id)
    
    def get_saved_view(self, id: int) -> PaperlessSavedView:
        return self.get(PaperlessSavedView, id)
    
    def get_document(self, id: int) -> PaperlessDocument:
        return self.get(PaperlessDocument, id)
    
    def get_storage_path(self, id: int) -> PaperlessStoragePath:
        return self.get(PaperlessStoragePath, id)
    
    def get_group(self, id: int) -> PaperlessGroup:
        return self.get(PaperlessGroup, id)
    
    def get_mail_account(self, id: int) -> PaperlessMailAccount:
        return self.get(PaperlessMailAccount, id)
    
    def get_mail_rule(self, id: int) -> PaperlessMailRule:
        return self.get(PaperlessMailRule, id)
    

    def get_tasks(self) -> List[PaperlessTask]:
        response = self._http_get(f"{self.basepath}/{PaperlessTask._endpoint}/", format="json")
        return [PaperlessTask(**item) for item in response]
    
    def get_custom_field(self, id:int) -> PaperlessCustomField:
        return self.get(PaperlessCustomField, id)