import hmac

from auth.application.interfaces.session_token_hasher import SessionTokenHasher
from auth.domain.entities.session import SessionToken, SessionTokenHash
from auth.entrypoint.config import SessionConfig


class SessionTokenHasherHmacSha256(SessionTokenHasher):
    def __init__(self, config: SessionConfig):
        self._secret = config.token_hash_secret.encode("utf-8")

    def hash(self, token: SessionToken) -> SessionTokenHash:
        return SessionTokenHash(
            hmac.digest(self._secret, token.encode("utf-8"), "sha256").hex()
        )
