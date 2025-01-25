from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, status

from auth.application.interactors.log_out import LogOutInteractor

log_out_router = APIRouter()


@log_out_router.delete(
    "/logout",
    status_code=status.HTTP_200_OK,
)
@inject
async def logout(interactor: FromDishka[LogOutInteractor]) -> None:
    return await interactor()
