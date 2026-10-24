from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter

from auth.application.errors import UnauthenticatedError
from auth.application.interactors.get_me import GetMeInteractor, GetMeResponse
from auth.presentation.http.base.error_response import get_error_responses
from auth.presentation.http.base.response import DataResponse

me_router = APIRouter()


@me_router.get(
    "/me",
    tags=["Users"],
    responses=get_error_responses(UnauthenticatedError),
)
@inject
async def get_me(
    interactor: FromDishka[GetMeInteractor],
) -> DataResponse[GetMeResponse]:
    result = await interactor()
    return DataResponse(data=result)
