from fastapi import APIRouter

from app.api.routes import (
    login,
    private,
    users,
    utils,
    agricultores,
    setores,
    aparelhos,
    controladores,
    comandos,
)
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(agricultores.router)
api_router.include_router(setores.router)
api_router.include_router(aparelhos.router)
api_router.include_router(controladores.router)
api_router.include_router(comandos.router)


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
