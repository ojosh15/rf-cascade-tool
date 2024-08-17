from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router


def register_app():
    app = FastAPI(title="rfcascade")
    app.include_router(router)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app
