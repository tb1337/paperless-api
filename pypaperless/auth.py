from aiohttp import ClientSession, ClientResponse
import base64

class Auth:
    """Class to make authenticated requests."""

    token: str = ""
    basic_auth: str = ""

    def __init__(self, endpoint: str, token: str = None, username: str = None, password: str = None):
        """Initialize the auth."""
        self.basepath = endpoint
        if token:
            self.token = token
        if username and password:
            self.basic_auth = base64.b64encode(f"{username}:{password}".encode()).decode()

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
        if self.token:
            headers["authorization"] = f"Token {self.token}"
        else:
            headers["authorization"] = f"Basic {self.basic_auth}"

        return await session.request(
            method, uri, **kwargs, headers=headers,
        )
