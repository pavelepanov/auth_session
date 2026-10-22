from fastapi import Request

from auth.application.interfaces.client_session_transport import ClientSessionTransport
from auth.domain.entities.session import SessionToken
from auth.presentation.http.base.cookie_params import CookieParams


class ClientSessionTransportCookie(ClientSessionTransport):
    def __init__(self, request: Request, cookie_params: CookieParams):
        self._request = request
        self._cookie_params = cookie_params

    async def get_session(self) -> SessionToken | None:
        session_token = self._request.cookies.get(self._cookie_params.name)
        if session_token is None:
            return None

        if not session_token:
            return None

        return SessionToken(session_token)

    async def set_session(self, session_token: SessionToken) -> None:
        self._request.state.new_session_token = session_token
        self._request.state.session_cookie_params = self._cookie_params

    async def clear_session(self) -> None:
        self._request.state.delete_session_token = True
        self._request.state.session_cookie_params = self._cookie_params
