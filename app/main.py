import logging
import uvicorn
from app.register import register_app

app = register_app()

def main():
    logging.basicConfig(level=logging.INFO)

    try:
        uvicorn.run(
            app="app.main:app",
            host="0.0.0.0",
            port=5000,
            reload=True,
        )
    except Exception as e:
        raise e