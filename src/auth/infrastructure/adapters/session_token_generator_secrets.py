from secrets import token_urlsafe

from auth.application.interfaces.session_token_generator import SessionTokenGenerator
from auth.domain.entities.session import SessionToken


class SessionTokenGeneratorSecrets(SessionTokenGenerator):
    def generate(self) -> SessionToken:
        return SessionToken(token_urlsafe(32))
