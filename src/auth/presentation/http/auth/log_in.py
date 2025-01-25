from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, status

from auth.application.interactors.log_in import LogInInteractor, LogInRequest

log_in_router = APIRouter()


@log_in_router.post(
    "/login",
    status_code=status.HTTP_200_OK,
)
@inject
async def login(
    request_data: LogInRequest,
    interactor: FromDishka[LogInInteractor],
) -> None:
    return await interactor(request_data)
