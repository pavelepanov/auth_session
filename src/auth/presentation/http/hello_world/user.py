from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, status

from auth.application.interactors.user_hello_world import (
    UserHelloWorldInteractor,
    UserHelloWorldResponse,
)

user_hello_world_router = APIRouter()


@user_hello_world_router.get("/user", status_code=status.HTTP_200_OK)
@inject
async def user_hello_world(
    interactor: FromDishka[UserHelloWorldInteractor],
) -> UserHelloWorldResponse:
    return await interactor()
