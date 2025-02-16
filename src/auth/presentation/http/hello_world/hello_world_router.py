from fastapi import APIRouter

from auth.presentation.http.hello_world.admin import admin_hello_world_router
from auth.presentation.http.hello_world.user import user_hello_world_router

hello_world_router = APIRouter(
    prefix="/hello_world",
    tags=["Hello world"],
)

hello_world_sub_routers = (user_hello_world_router, admin_hello_world_router)

for router in hello_world_sub_routers:
    hello_world_router.include_router(router)
