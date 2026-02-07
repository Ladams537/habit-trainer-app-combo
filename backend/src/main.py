from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.middleware import setup_middleware
from src.api.router import api_router
from src.modules.fitness.seed_exercises import seed_built_in_exercises
from src.shared.database import async_session


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Seed built-in exercises on startup
    async with async_session() as db:
        count = await seed_built_in_exercises(db)
        if count > 0:
            await db.commit()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="Personal Trainer API", version="0.1.0", lifespan=lifespan)
    setup_middleware(app)
    app.include_router(api_router)

    @app.get("/api/health")
    async def health_check():
        return {"status": "ok"}

    return app


app = create_app()
