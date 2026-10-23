from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, status

from auth.application.errors import PermissionDeniedError, UnauthenticatedError
from auth.application.interactors.user_hello_world import (
    UserHelloWorldInteractor,
    UserHelloWorldResponse,
)
from auth.presentation.http.base.error_response import get_error_responses
from auth.presentation.http.base.response import DataResponse

user_hello_world_router = APIRouter()


@user_hello_world_router.get(
    "/user",
    status_code=status.HTTP_200_OK,
    responses=get_error_responses(UnauthenticatedError, PermissionDeniedError),
)
@inject
async def user_hello_world(
    interactor: FromDishka[UserHelloWorldInteractor],
) -> DataResponse[UserHelloWorldResponse]:
    return DataResponse(data=await interactor())
