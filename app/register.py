from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router
from app.config import config


def register_app():
    app = FastAPI(title="rfcascade")
    app.servers = [
        {"url": config.API_PREFIX, "description": "Default"},
    ]
    app.root_path = config.API_PREFIX
    app.include_router(router)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app
