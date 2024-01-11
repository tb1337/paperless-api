"""Simple router for faking Paperless routes."""

from aiohttp.web_exceptions import HTTPNotFound
from fastapi import FastAPI, Request

from tests.data.v0_0_0 import V0_0_0_CORRESPONDENTS, V0_0_0_DOCUMENT_TYPES, V0_0_0_PATHS
from tests.data.v1_8_0 import V1_8_0_PATHS, V1_8_0_STORAGE_PATHS

PATCHWORK = {
    "0.0.0": {
        "PATHS": V0_0_0_PATHS,
        "CORRESPONDENTS": V0_0_0_CORRESPONDENTS,
        "DOCUMENT_TYPES": V0_0_0_DOCUMENT_TYPES,
    },
    "1.8.0": {
        "PATHS": V0_0_0_PATHS | V1_8_0_PATHS,
        "STORAGE_PATHS": V1_8_0_STORAGE_PATHS,
    },
}


def _data_helper(req: Request, key: str):
    """Get data from patchwork."""
    return PATCHWORK.setdefault(req.headers["x-test-ver"], "0.0.0")[key]


FakePaperlessAPI = FastAPI()


@FakePaperlessAPI.get("/api/")
async def get_index(req: Request):
    """Index page."""
    return _data_helper(req, "PATHS")


@FakePaperlessAPI.get("/api/{resource}/")
async def get_resource(req: Request, resource: str):
    """Get resource."""
    return _data_helper(req, resource.upper())


@FakePaperlessAPI.post("/api/{resource}/")
async def post_resource(req: Request, resource: str):
    """Post resource."""
    payload = await req.json()
    data = _data_helper(req, resource.upper())
    payload["id"] = len(data["all"]) + 1
    data["all"].append(payload["id"])
    data["results"].append(payload)
    return payload


@FakePaperlessAPI.get("/api/{resource}/{item:int}/")
async def get_resource_item(req: Request, resource: str, item: int):
    """Get resource item."""
    data = _data_helper(req, resource.upper())
    for result in data["results"]:
        if result["id"] == item:
            return result
    raise HTTPNotFound()


@FakePaperlessAPI.put("/api/{resource}/{item:int}/")
async def put_resource_item(req: Request, resource: str, item: int):
    """Put resource item."""
    payload = await req.json()
    data = _data_helper(req, resource.upper())
    for result in data["results"]:
        if result["id"] == item:
            result = payload  # noqa: PLW2901
            return result
    return HTTPNotFound()


@FakePaperlessAPI.delete("/api/{resource}/{item:int}/")
async def delete_resource_item(req: Request, resource: str, item: int):
    """Delete resource item."""
    data = _data_helper(req, resource.upper())
    for idx, result in enumerate(data["results"]):
        if result["id"] == item:
            data["results"].pop(idx)
            break
    return HTTPNotFound()
