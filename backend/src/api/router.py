from fastapi import APIRouter

from src.modules.auth.routes import router as auth_router
from src.modules.fitness.routes import router as fitness_router
from src.modules.habits.routes import router as habits_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(habits_router)
api_router.include_router(fitness_router)
