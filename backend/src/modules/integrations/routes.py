from fastapi import APIRouter, HTTPException, status

from src.api.dependencies import DB, CurrentUser
from src.modules.integrations.schemas import IntegrationStatus, StravaSyncResult
from src.modules.integrations.service import IntegrationService
from src.modules.integrations.strava import get_auth_url

router = APIRouter(prefix="/api/integrations", tags=["integrations"])


@router.get("/strava/auth-url")
async def strava_auth_url():
    return {"url": get_auth_url()}


@router.post("/strava/callback")
async def strava_callback(code: str, current_user: CurrentUser, db: DB):
    service = IntegrationService(db)
    try:
        await service.connect_strava(current_user.id, code)
        return {"connected": True}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to connect Strava: {e}",
        )


@router.delete("/strava", status_code=status.HTTP_204_NO_CONTENT)
async def disconnect_strava(current_user: CurrentUser, db: DB):
    service = IntegrationService(db)
    await service.disconnect_strava(current_user.id)


@router.get("/status", response_model=list[IntegrationStatus])
async def get_status(current_user: CurrentUser, db: DB):
    service = IntegrationService(db)
    strava_status = await service.get_integration_status(current_user.id, "strava")
    return [strava_status]


@router.post("/strava/sync", response_model=StravaSyncResult)
async def sync_strava(current_user: CurrentUser, db: DB):
    service = IntegrationService(db)
    result = await service.sync_strava_activities(current_user.id)
    return result
