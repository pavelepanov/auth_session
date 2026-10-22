from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, status
from pydantic import BaseModel, EmailStr

from auth.application.interactors.log_in import LogInInteractor, LogInRequest

log_in_router = APIRouter()


class LogInRequestModel(BaseModel):
    email: EmailStr
    raw_password: str


@log_in_router.post(
    "/login",
    status_code=status.HTTP_200_OK,
)
@inject
async def login(
    request_data: LogInRequestModel,
    interactor: FromDishka[LogInInteractor],
) -> None:
    return await interactor(
        LogInRequest(email=request_data.email, raw_password=request_data.raw_password)
    )
