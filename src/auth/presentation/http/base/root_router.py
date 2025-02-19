from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from auth.presentation.http.auth.auth_router import auth_router
from auth.presentation.http.hello_world.hello_world_router import hello_world_router

root_router = APIRouter()


@root_router.get("/", tags=["General"])
async def redirect_to_docs() -> RedirectResponse:
    return RedirectResponse(url="docs/")


root_sub_routers = (auth_router, hello_world_router)

for router in root_sub_routers:
    root_router.include_router(router)
