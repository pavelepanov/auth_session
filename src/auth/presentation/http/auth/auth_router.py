from fastapi import APIRouter

from auth.presentation.http.auth.sign_up import sign_up_router

auth_router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

auth_sub_routers = (sign_up_router,)

for router in auth_sub_routers:
    auth_router.include_router(router)
