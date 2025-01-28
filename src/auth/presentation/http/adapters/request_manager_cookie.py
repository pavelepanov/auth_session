from fastapi.requests import Request

from auth.application.interfaces.request_manager import RequestManager
from auth.domain.entities.session import SessionId
from auth.presentation.http.base.cookie_params import CookieParams


class RequestManagerCookie(RequestManager):
    def __init__(
        self,
        request: Request,
        cookie_params: CookieParams,
    ):
        self._request = request
        self._cookie_params = cookie_params

    def get_session_id_from_request(self) -> SessionId | None:
        return self._request.cookies.get("id")

    def add_session_id_to_request(self, session_id: SessionId) -> None:
        self._request.state.new_session_id = session_id
        self._request.state.cookie_params = {
            "secure": self._cookie_params.secure,
            "samesite": self._cookie_params.samesite,
        }

    def delete_session_from_request(self) -> None:
        self._request.state.delete_session_id = True
