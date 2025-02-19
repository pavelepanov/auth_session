from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, status

from auth.application.interactors.admin_hello_world import (
    AdminHelloWorldInteractor,
    AdminHelloWorldResponse,
)

admin_hello_world_router = APIRouter()


@admin_hello_world_router.get("/admin", status_code=status.HTTP_200_OK)
@inject
async def admin_hello_world(
    interactor: FromDishka[AdminHelloWorldInteractor],
) -> AdminHelloWorldResponse:
    return await interactor()
