from fastapi import APIRouter

from app.api.endpoints import auth, projects, paths, components
from app.config import config

router = APIRouter()

router.include_router(auth.router)
router.include_router(projects.router)
router.include_router(paths.router)
router.include_router(components.router)