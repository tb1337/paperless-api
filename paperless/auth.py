from aiohttp import ClientSession, ClientResponse


class Auth:
    """Class to make authenticated requests."""

    def __init__(self, websession: ClientSession, path: str, access_token: str):
        """Initialize the auth."""
        self.websession = websession
        self.basepath = path
        self.access_token = access_token

    async def request(self, method: str, path: str, **kwargs) -> ClientResponse:
        uri = f"{self.basepath}/{path}/"
        return await self.__request(method, uri, **kwargs)

    async def request_raw(self, method: str, uri: str, **kwargs) -> ClientResponse:
        return await self.__request(method, uri, **kwargs)

    async def __request(self, method: str, uri: str, **kwargs) -> ClientResponse:
        """Make a request."""
        headers = kwargs.get("headers")
        params = kwargs.get("params")

        if headers is None:
            headers = {}
        else:
            headers = dict(headers)

        if params is None:
            params = {}
        else:
            params = dict(params)

        params["format"] = "json"
        headers["authorization"] = f"Token {self.access_token}"

        return await self.websession.request(
            method, uri, **kwargs, headers=headers,
        )
