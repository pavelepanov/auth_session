from bcrypt import checkpw, gensalt, hashpw

from auth.application.interfaces.password_hasher import PasswordHasher
from auth.domain.entities.user import PasswordHash, RawPassword


class PasswordHasherBcrypt(PasswordHasher):
    def hash(self, raw_password: RawPassword) -> PasswordHash:
        salt = gensalt()

        password_hash = hashpw(raw_password.encode("utf-8"), salt)

        return PasswordHash(password_hash.decode("utf-8"))

    def verify(self, raw_password: RawPassword, password_hash: PasswordHash) -> bool:
        return checkpw(raw_password.encode("utf-8"), password_hash.encode("utf-8"))
