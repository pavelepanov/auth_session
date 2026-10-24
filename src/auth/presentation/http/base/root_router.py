from fastapi import APIRouter

from auth.presentation.http.auth.auth_router import auth_router
from auth.presentation.http.hello_world.hello_world_router import hello_world_router
from auth.presentation.http.me import me_router

root_router = APIRouter()


@root_router.get("/health", include_in_schema=False)
async def health() -> dict[str, str]:
    return {"status": "ok"}


root_sub_routers = (auth_router, hello_world_router, me_router)

for router in root_sub_routers:
    root_router.include_router(router)
