from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, status
from pydantic import BaseModel, EmailStr

from auth.application.interactors.sign_up import (
    SignUpInteractor,
    SignUpRequest,
    SignUpResponse,
)

sign_up_router = APIRouter()


class SignUpRequestModel(BaseModel):
    email: EmailStr
    raw_password: str


@sign_up_router.post("/signup", status_code=status.HTTP_201_CREATED)
@inject
async def sign_up(
    request_data: SignUpRequestModel,
    interactor: FromDishka[SignUpInteractor],
) -> SignUpResponse:
    return await interactor(
        SignUpRequest(email=request_data.email, raw_password=request_data.raw_password)
    )
