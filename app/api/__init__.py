from fastapi import APIRouter

from api.endpoints import projects
from config import config

router = APIRouter(prefix=config.API_PREFIX)

router.include_router(projects.router)
# router.include_router(supported_radios.router)