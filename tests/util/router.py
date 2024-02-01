"""Simple router for faking Paperless routes."""

import datetime
import random
import uuid

from aiohttp.web_exceptions import HTTPBadRequest, HTTPNotFound
from fastapi import FastAPI, Request, Response

from tests.data.v0_0_0 import (
    V0_0_0_CORRESPONDENTS,
    V0_0_0_DOCUMENT_SUGGESTIONS,
    V0_0_0_DOCUMENT_TYPES,
    V0_0_0_DOCUMENTS,
    V0_0_0_DOCUMENTS_METADATA,
    V0_0_0_DOCUMENTS_SEARCH,
    V0_0_0_GROUPS,
    V0_0_0_MAIL_ACCOUNTS,
    V0_0_0_MAIL_RULES,
    V0_0_0_PATHS,
    V0_0_0_SAVED_VIEWS,
    V0_0_0_TAGS,
    V0_0_0_TASKS,
    V0_0_0_TOKEN,
    V0_0_0_USERS,
)
from tests.data.v1_8_0 import V1_8_0_PATHS, V1_8_0_STORAGE_PATHS
from tests.data.v1_17_0 import V1_17_0_DOCUMENT_NOTES
from tests.data.v2_0_0 import (
    V2_0_0_CONFIG,
    V2_0_0_CONSUMPTION_TEMPLATES,
    V2_0_0_CUSTOM_FIELDS,
    V2_0_0_PATHS,
    V2_0_0_SHARE_LINKS,
)
from tests.data.v2_3_0 import (
    V2_3_0_PATHS,
    V2_3_0_WORKFLOW_ACTIONS,
    V2_3_0_WORKFLOW_TRIGGERS,
    V2_3_0_WORKFLOWS,
)

# mypy: ignore-errors

PATCHWORK = {
    "0.0.0": {
        "PATHS": V0_0_0_PATHS,
        "CORRESPONDENTS": V0_0_0_CORRESPONDENTS,
        "DOCUMENTS": V0_0_0_DOCUMENTS,
        "DOCUMENTS_METADATA": V0_0_0_DOCUMENTS_METADATA,
        "DOCUMENTS_SEARCH": V0_0_0_DOCUMENTS_SEARCH,
        "DOCUMENTS_SUGGESTIONS": V0_0_0_DOCUMENT_SUGGESTIONS,
        "DOCUMENT_TYPES": V0_0_0_DOCUMENT_TYPES,
        "GROUPS": V0_0_0_GROUPS,
        "MAIL_ACCOUNTS": V0_0_0_MAIL_ACCOUNTS,
        "MAIL_RULES": V0_0_0_MAIL_RULES,
        "SAVED_VIEWS": V0_0_0_SAVED_VIEWS,
        "TAGS": V0_0_0_TAGS,
        "TASKS": V0_0_0_TASKS,
        "TOKEN": V0_0_0_TOKEN,
        "USERS": V0_0_0_USERS,
    },
    "1.8.0": {
        "PATHS": V0_0_0_PATHS | V1_8_0_PATHS,
        "STORAGE_PATHS": V1_8_0_STORAGE_PATHS,
    },
    "1.17.0": {
        "PATHS": "1.8.0",
        "DOCUMENTS": V0_0_0_DOCUMENTS,
        "DOCUMENT_NOTES": V1_17_0_DOCUMENT_NOTES,
    },
    "2.0.0": {
        "PATHS": V0_0_0_PATHS | V1_8_0_PATHS | V2_0_0_PATHS,
        "CONFIG": V2_0_0_CONFIG,
        "CONSUMPTION_TEMPLATES": V2_0_0_CONSUMPTION_TEMPLATES,
        "CUSTOM_FIELDS": V2_0_0_CUSTOM_FIELDS,
        "SHARE_LINKS": V2_0_0_SHARE_LINKS,
    },
    "2.3.0": {
        "PATHS": V0_0_0_PATHS | V1_8_0_PATHS | V2_0_0_PATHS | V2_3_0_PATHS,
        "WORKFLOWS": V2_3_0_WORKFLOWS,
        "WORKFLOW_ACTIONS": V2_3_0_WORKFLOW_ACTIONS,
        "WORKFLOW_TRIGGERS": V2_3_0_WORKFLOW_TRIGGERS,
    },
}


def _api_switcher(req: Request, key: str):
    """Get data from patchwork."""
    version = req.headers["x-test-ver"]
    if version not in PATCHWORK:
        version = "0.0.0"
    if key not in PATCHWORK[version]:
        return PATCHWORK["0.0.0"][key]
    value = PATCHWORK[version][key]
    if isinstance(value, str):
        return PATCHWORK[value][key]
    return value


FakePaperlessAPI = FastAPI()


# test http route with parameterable content, content type and status codes
@FakePaperlessAPI.get("/test/http/{status:int}/")
async def get_http_error(req: Request, status: int):
    """Get bad request."""
    content = req.query_params.get("response_content", f"http error {status}")
    content_type = req.query_params.get("content_type", "application/json")
    return Response(
        status_code=status,
        content=content,
        headers={"Content-Type": content_type},
    )


# index route
@FakePaperlessAPI.get("/api/")
async def get_index(req: Request):
    """Index page."""
    return _api_switcher(req, "PATHS")


# token route
@FakePaperlessAPI.post("/api/token/")
async def post_token(req: Request):
    """Post credentials to get new api token."""
    content = req.query_params.get("response_content", "empty")
    status = req.query_params.get("status", 200)
    return Response(
        status_code=int(status),
        content=content,
        headers={"Content-Type": "application/json"},
    )


# static routes for special cases
@FakePaperlessAPI.post("/api/documents/post_document/")
async def post_document(req: Request):
    """Post document."""
    payload = await req.json()
    if "document" not in payload:
        raise HTTPBadRequest()
    # create document
    data = _api_switcher(req, "DOCUMENTS")
    task_id = uuid.uuid4()
    payload.setdefault("title", f"New Document {task_id}")
    payload.setdefault("created", datetime.datetime.now().isoformat())
    payload.setdefault("correspondent", None)
    payload.setdefault("document_type", None)
    payload.setdefault("archive_serial_number", None)
    payload.setdefault("storage_path", None)
    payload.setdefault("tags", [])
    new = {
        "id": len(data["all"]) + 1,
        "correspondent": payload["correspondent"],
        "document_type": payload["document_type"],
        "storage_path": payload["storage_path"],
        "title": payload["title"],
        "content": payload["document"],
        "tags": payload["tags"],
        "created": payload["created"],
        "created_date": datetime.datetime.fromisoformat(payload["created"]).date().isoformat(),
        "modified": datetime.datetime.now().isoformat(),
        "added": datetime.datetime.now().isoformat(),
        "archive_serial_number": payload["archive_serial_number"],
        "original_file_name": f"{task_id}.pdf",
        "archived_file_name": f"{task_id}_archived.pdf",
        "owner": 1,
        "user_can_change": True,
        "notes": [],
        "custom_fields": [],
    }
    data["all"].append(new["id"])
    data["results"].append(new)
    # create task
    data = _api_switcher(req, "TASKS")
    task = {
        "id": len(data) + 1,
        "task_id": f"{task_id}",
        "task_file_name": new["original_file_name"],
        "date_created": new["created"],
        "date_done": new["added"],
        "type": "file",
        "status": "SUCCESS",
        "result": f"Success. New document id {new['id']} created",
        "acknowledged": False,
        "related_document": new["id"],
    }
    data.append(task)
    return f"{task_id}"


@FakePaperlessAPI.get("/api/documents/next_asn/")
async def get_documents_next_asn(req: Request):
    """Get documents next asn."""
    status = req.query_params.get("status", 200)
    return Response(
        status_code=int(status),
        content=str(random.randint(1, 1337)),
    )


@FakePaperlessAPI.get("/api/documents/{pk:int}/metadata/")
async def get_documents_meta(req: Request, pk: int):
    """Get documents meta."""
    data = _api_switcher(req, "DOCUMENTS")
    if not data["all"].count(pk):
        raise HTTPNotFound()
    data = _api_switcher(req, "DOCUMENTS_METADATA")
    data["media_filename"] = f"{pk}.pdf"
    return data


@FakePaperlessAPI.get("/api/documents/{pk:int}/suggestions/")
async def get_documents_suggestions(req: Request, pk: int):
    """Get documents suggestions."""
    data = _api_switcher(req, "DOCUMENTS")
    if not data["all"].count(pk):
        raise HTTPNotFound()
    data = _api_switcher(req, "DOCUMENTS_SUGGESTIONS")
    return data


@FakePaperlessAPI.get("/api/documents/{pk:int}/thumb/")
@FakePaperlessAPI.get("/api/documents/{pk:int}/preview/")
@FakePaperlessAPI.get("/api/documents/{pk:int}/download/")
async def get_documents_files(req: Request, pk: int):
    """Get documents files."""
    data = _api_switcher(req, "DOCUMENTS")
    if not data["all"].count(pk):
        raise HTTPNotFound()
    return Response(
        status_code=200,
        content=b"This is a file.",
        headers={
            "Content-Type": "application/pdf",
            "Content-Disposition": "attachment;any_filename.pdf",
        },
    )


@FakePaperlessAPI.get("/api/documents/{pk:int}/notes/")
@FakePaperlessAPI.post("/api/documents/{pk:int}/notes/")
async def get_documents_notes(
    req: Request, pk: int  # pylint: disable=unused-argument # noqa: ARG001
):
    """Get documents notes."""
    data = _api_switcher(req, "DOCUMENT_NOTES")
    return data


@FakePaperlessAPI.delete("/api/documents/{pk:int}/notes/")
async def post_delete_documents_notes(
    req: Request, pk: int  # pylint: disable=unused-argument # noqa: ARG001
):
    """Get documents notes."""
    return Response(status_code=204)


@FakePaperlessAPI.get("/api/tasks/")
async def get_tasks(req: Request):
    """Get tasks resource."""
    data = _api_switcher(req, "TASKS")
    if "task_id" in req.query_params:
        single = []
        for task in data:
            if task["task_id"] == req.query_params["task_id"]:
                single.append(task)
        return single
    return data


# the following routes must be declared after static routes, as they handle common cases
@FakePaperlessAPI.get("/api/{resource}/")
async def get_resource(req: Request, resource: str):
    """Get resource."""
    if resource == "documents":
        query = req.query_params.get("query", None)
        more_like = req.query_params.get("more_like_id", None)
        if query or more_like:
            data = _api_switcher(req, f"{resource}_search".upper())
            return data

    if resource == "tasks":
        return {}

    data = _api_switcher(req, resource.upper())
    return data


@FakePaperlessAPI.post("/api/{resource}/")
async def post_resource(req: Request, resource: str):
    """Post resource."""
    payload = await req.json()
    data = _api_switcher(req, resource.upper())
    payload["id"] = len(data["all"]) + 1
    data["all"].append(payload["id"])
    data["results"].append(payload)
    return payload


@FakePaperlessAPI.get("/api/{resource}/{item:int}/")
async def get_resource_item(req: Request, resource: str, item: int):
    """Get resource item."""
    data = _api_switcher(req, resource.upper())
    # tasks is list, else dict
    iterable = data["results"] if isinstance(data, dict) else data
    for result in iterable:
        if result["id"] == item:
            return result
    raise HTTPNotFound()


@FakePaperlessAPI.delete("/api/{resource}/{item:int}/")
async def delete_resource_item(req: Request, resource: str, item: int):
    """Delete resource item."""
    data = _api_switcher(req, resource.upper())
    for idx, result in enumerate(data["results"]):
        if result["id"] == item:
            data["results"].pop(idx)
            return Response(status_code=204)
    raise HTTPNotFound()


@FakePaperlessAPI.patch("/api/{resource}/{item:int}/")
async def patch_resource_item(req: Request, resource: str, item: int):
    """Patch resource item."""
    payload = await req.json()
    data = _api_switcher(req, resource.upper())
    for result in data["results"]:
        if result["id"] == item:
            for k, v in payload.items():
                result[k] = v
            return result
    raise HTTPNotFound()


@FakePaperlessAPI.put("/api/{resource}/{item:int}/")
async def put_resource_item(req: Request, resource: str, item: int):
    """Put resource item."""
    payload = await req.json()
    data = _api_switcher(req, resource.upper())
    for result in data["results"]:
        if result["id"] == item:
            result = payload  # noqa: PLW2901
            return result
    raise HTTPNotFound()
