from auth.domain.entities.session import SessionToken
from auth.entrypoint.config import SessionConfig
from auth.infrastructure.adapters.session_token_hasher_hmac_sha256 import (
    SessionTokenHasherHmacSha256,
)


class TestSessionTokenHasherHmacSha256:
    def test_hash_matches_known_hmac_sha256_vector(self) -> None:
        token = SessionToken("what do ya want for nothing?")
        hasher = SessionTokenHasherHmacSha256(SessionConfig(30, "Jefe"))

        hashed = hasher.hash(token)

        assert hashed == (
            "5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843"
        )
        assert len(hashed) == 64
        assert str(hashed) != str(token)

    def test_secret_and_token_change_hash(self, session_config: SessionConfig) -> None:
        first = SessionTokenHasherHmacSha256(session_config)
        second = SessionTokenHasherHmacSha256(SessionConfig(30, "other-secret"))

        assert first.hash(SessionToken("a")) != first.hash(SessionToken("b"))
        assert first.hash(SessionToken("a")) != second.hash(SessionToken("a"))
