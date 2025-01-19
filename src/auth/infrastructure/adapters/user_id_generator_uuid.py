from uuid import UUID, uuid4

from auth.application.interfaces.user_id_generator import UserIdGenerator


class UserIdGeneratorImpl(UserIdGenerator):
    def __call__(self) -> UUID:
        return uuid4()
