from fastapi.routing import APIRouter

from exercise.web.api import admin, dummy, echo, monitoring

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(echo.router, prefix="/echo", tags=["echo"])
api_router.include_router(dummy.router, prefix="/dummy", tags=["dummy"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
