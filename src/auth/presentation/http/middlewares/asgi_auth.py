from http.cookies import SimpleCookie
from typing import Any, Literal

from fastapi import FastAPI
from starlette.datastructures import MutableHeaders
from starlette.requests import Request
from starlette.types import Message, Receive, Scope, Send


class ASGIAuthMiddleware:
    def __init__(self, app: FastAPI):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request: Request = Request(scope)

        async def modify_cookies(message: Message) -> None:
            if message["type"] != "http.response.start":
                await send(message)
                return

            headers: MutableHeaders = MutableHeaders(scope=message)

            self._set_id_cookie(request, headers)
            self._delete_id_cookie(request, headers)

            await send(message)

        await self.app(scope, receive, modify_cookies)

    def _set_id_cookie(
        self,
        request: Request,
        headers: MutableHeaders,
    ) -> None:
        new_session_id: str | None = getattr(request.state, "new_session_id", None)

        if new_session_id is None:
            return

        cookie_params: dict[str, Any] = getattr(request.state, "cookie_params", None)

        is_cookie_secure: bool = cookie_params.get("secure", False)
        cookie_samesite: Literal["strict"] | None = cookie_params.get("samesite", None)

        cookie: SimpleCookie = SimpleCookie()

        cookie["id"] = new_session_id
        cookie["id"]["path"] = "/"
        cookie["id"]["httponly"] = True

        if is_cookie_secure:
            cookie["id"]["secure"] = True

        if cookie_samesite is not None:
            cookie["id"]["samesite"] = cookie_samesite

        headers.append("Set-Cookie", cookie.output(header="").strip())

    def _delete_id_cookie(self, request: Request, headers: MutableHeaders) -> None:
        is_delete_id: bool = getattr(request.state, "delete_session_id", False)
        if not is_delete_id:
            return

        cookie: SimpleCookie = SimpleCookie()

        cookie["id"] = ""
        cookie["id"]["path"] = "/"
        cookie["id"]["httponly"] = True
        cookie["id"]["max-age"] = 0

        headers.append("Set-Cookie", cookie.output(header="").strip())
