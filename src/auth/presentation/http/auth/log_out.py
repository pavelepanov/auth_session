from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, status

from auth.application.interactors.log_out import LogOutInteractor
from auth.presentation.http.base.error_response import get_error_responses

log_out_router = APIRouter()


@log_out_router.delete(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=get_error_responses(),
)
@inject
async def logout(interactor: FromDishka[LogOutInteractor]) -> None:
    return await interactor()
