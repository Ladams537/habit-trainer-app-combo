from fastapi import APIRouter

from src.modules.auth.routes import router as auth_router
from src.modules.fitness.routes import router as fitness_router
from src.modules.habits.routes import router as habits_router
from src.modules.analytics.routes import router as analytics_router
from src.modules.skills.routes import router as skills_router
from src.modules.export.routes import router as export_router
from src.modules.integrations.routes import router as integrations_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(habits_router)
api_router.include_router(fitness_router)
api_router.include_router(skills_router)
api_router.include_router(analytics_router)
api_router.include_router(export_router)
api_router.include_router(integrations_router)
