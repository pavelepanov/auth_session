from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, status
from pydantic import BaseModel, EmailStr

from auth.application.errors import AlreadyAuthenticatedError, InvalidCredentialsError
from auth.application.interactors.log_in import LogInInteractor, LogInRequest
from auth.presentation.http.base.error_response import get_error_responses
from auth.presentation.http.base.response import DataResponse

log_in_router = APIRouter()


class LogInRequestModel(BaseModel):
    email: EmailStr
    raw_password: str


@log_in_router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    responses=get_error_responses(
        InvalidCredentialsError,
        AlreadyAuthenticatedError,
        include_input_errors=True,
    ),
)
@inject
async def login(
    request_data: LogInRequestModel,
    interactor: FromDishka[LogInInteractor],
) -> DataResponse[None]:
    await interactor(
        LogInRequest(email=request_data.email, raw_password=request_data.raw_password)
    )
    return DataResponse(data=None)
