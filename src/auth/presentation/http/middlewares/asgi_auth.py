from starlette.datastructures import MutableHeaders
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from auth.domain.entities.session import SessionToken
from auth.presentation.http.base.cookie_params import CookieParams


class ASGIAuthMiddleware:
    def __init__(self, app: ASGIApp):
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

            self._apply_session_cookie(request, headers)

            await send(message)

        await self.app(scope, receive, modify_cookies)

    def _apply_session_cookie(self, request: Request, headers: MutableHeaders) -> None:
        token: SessionToken | None = getattr(request.state, "new_session_token", None)
        delete_token: bool = getattr(request.state, "delete_session_token", False)
        if token is None and not delete_token:
            return

        params: CookieParams = request.state.session_cookie_params
        response = Response()
        if token is None:
            response.delete_cookie(
                params.name,
                path=params.path,
                secure=params.secure,
                httponly=params.httponly,
                samesite=params.samesite,
            )
        else:
            response.set_cookie(
                params.name,
                token,
                max_age=params.max_age,
                path=params.path,
                secure=params.secure,
                httponly=params.httponly,
                samesite=params.samesite,
            )

        for value in response.headers.getlist("set-cookie"):
            headers.append("set-cookie", value)
