from fastapi import APIRouter

from auth.presentation.http.auth.log_in import log_in_router
from auth.presentation.http.auth.log_out import log_out_router
from auth.presentation.http.auth.sign_up import sign_up_router
from auth.presentation.http.auth.verification import verification_router

auth_router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

auth_sub_routers = (sign_up_router, log_in_router, log_out_router, verification_router)

for router in auth_sub_routers:
    auth_router.include_router(router)
