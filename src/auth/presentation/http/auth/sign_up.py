from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, status

from auth.application.interactors.sign_up import (SignUpInteractor,
                                                  SignUpRequest,
                                                  SignUpResponse)

sign_up_router = APIRouter()


@sign_up_router.post("/signup", status_code=status.HTTP_201_CREATED)
@inject
async def sign_up(
    request_data: SignUpRequest,
    interactor: FromDishka[SignUpInteractor],
) -> SignUpResponse:
    return await interactor(request_data)
