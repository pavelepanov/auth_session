from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, status

from auth.application.interactors.verification import (
    VerificationInteractor,
    VerificationRequest,
)

verification_router = APIRouter()


@verification_router.post(
    "verification/{user_id}",
    status_code=status.HTTP_200_OK,
)
@inject
async def verification(
    request_data: VerificationRequest, interactor: FromDishka[VerificationInteractor]
) -> None:
    return await interactor(request_data=request_data)
