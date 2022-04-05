from aiohttp import ClientSession, ClientResponse


class Auth:
    """Class to make authenticated requests."""

    def __init__(self, endpoint: str, token: str):
        """Initialize the auth."""
        self.basepath = endpoint
        self.token = token

    async def request(self, session: ClientSession, method: str, path: str, **kwargs) -> ClientResponse:
        uri = f"{self.basepath}/{path}/"
        return await self.__request(session, method, uri, **kwargs)

    async def request_raw(self, session: ClientSession, method: str, uri: str, **kwargs) -> ClientResponse:
        return await self.__request(session, method, uri, **kwargs)

    async def __request(self, session: ClientSession, method: str, uri: str, **kwargs) -> ClientResponse:
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
        headers["authorization"] = f"Token {self.token}"

        return await session.request(
            method, uri, **kwargs, headers=headers,
        )
