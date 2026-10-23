from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, status

from auth.application.errors import PermissionDeniedError, UnauthenticatedError
from auth.application.interactors.admin_hello_world import (
    AdminHelloWorldInteractor,
    AdminHelloWorldResponse,
)
from auth.presentation.http.base.error_response import get_error_responses
from auth.presentation.http.base.response import DataResponse

admin_hello_world_router = APIRouter()


@admin_hello_world_router.get(
    "/admin",
    status_code=status.HTTP_200_OK,
    responses=get_error_responses(UnauthenticatedError, PermissionDeniedError),
)
@inject
async def admin_hello_world(
    interactor: FromDishka[AdminHelloWorldInteractor],
) -> DataResponse[AdminHelloWorldResponse]:
    result: AdminHelloWorldResponse = await interactor()
    return DataResponse(data=result)
