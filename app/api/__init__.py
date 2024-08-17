from fastapi import APIRouter

from app.api.endpoints import projects, paths, components
from app.config import config

router = APIRouter(prefix=config.API_PREFIX)

router.include_router(projects.router)
router.include_router(paths.router)
router.include_router(components.router)