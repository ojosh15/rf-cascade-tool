from fastapi import APIRouter

# from api.endpoints import radios, supported_radios
from config import config

router = APIRouter(prefix=config.API_PREFIX)

# router.include_router(radios.router)
# router.include_router(supported_radios.router)