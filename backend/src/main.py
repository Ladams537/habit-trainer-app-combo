from fastapi import FastAPI

from src.api.middleware import setup_middleware
from src.api.router import api_router


def create_app() -> FastAPI:
    app = FastAPI(title="Personal Trainer API", version="0.1.0")
    setup_middleware(app)
    app.include_router(api_router)

    @app.get("/api/health")
    async def health_check():
        return {"status": "ok"}

    return app


app = create_app()
