from typing import Iterable

from dishka import Provider

from auth.entrypoint.ioc.adapters import SqlaProvider, IdGeneratorsProvider, RedisProvider, AuthProvider
from auth.entrypoint.ioc.interactors import InteractorProvider


def get_providers() -> Iterable[Provider]:
    return (
        InteractorProvider(),
        SqlaProvider(),
        IdGeneratorsProvider(),
        RedisProvider(),
        AuthProvider(),
    )