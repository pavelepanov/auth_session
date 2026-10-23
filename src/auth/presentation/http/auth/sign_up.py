from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, status
from pydantic import BaseModel, EmailStr

from auth.application.errors import (
    AlreadyAuthenticatedError,
    InvalidPasswordError,
    UserEmailAlreadyExistsError,
)
from auth.application.interactors.sign_up import (
    SignUpInteractor,
    SignUpRequest,
    SignUpResponse,
)
from auth.presentation.http.base.error_response import get_error_responses
from auth.presentation.http.base.response import DataResponse

sign_up_router = APIRouter()


class SignUpRequestModel(BaseModel):
    email: EmailStr
    raw_password: str


@sign_up_router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
    responses=get_error_responses(
        AlreadyAuthenticatedError,
        UserEmailAlreadyExistsError,
        InvalidPasswordError,
        include_input_errors=True,
    ),
)
@inject
async def sign_up(
    request_data: SignUpRequestModel,
    interactor: FromDishka[SignUpInteractor],
) -> DataResponse[SignUpResponse]:
    result: SignUpResponse = await interactor(
        SignUpRequest(email=request_data.email, raw_password=request_data.raw_password)
    )
    return DataResponse(data=result)
