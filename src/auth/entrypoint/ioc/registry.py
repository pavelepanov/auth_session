from typing import Iterable

from dishka import Provider

from auth.entrypoint.ioc.adapters import (
    AuthProvider,
    ConfigProvider,
    IdGeneratorsProvider,
    RabbitMQProvider,
    SqlaProvider,
)
from auth.entrypoint.ioc.interactors import InteractorProvider


def get_providers() -> Iterable[Provider]:
    return (
        InteractorProvider(),
        SqlaProvider(),
        IdGeneratorsProvider(),
        AuthProvider(),
        ConfigProvider(),
        RabbitMQProvider(),
    )
