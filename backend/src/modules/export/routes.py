import uuid

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse, Response, StreamingResponse
from sqlalchemy import select

from src.api.dependencies import DB, CurrentUser
from src.modules.auth.models import User
from src.modules.export.ical import generate_ical_feed
from src.modules.export.service import ExportService

router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("/workouts")
async def export_workouts(current_user: CurrentUser, db: DB):
    service = ExportService(db)
    return StreamingResponse(
        service.export_workouts(current_user.id),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=workouts.csv"},
    )


@router.get("/habits")
async def export_habits(current_user: CurrentUser, db: DB):
    service = ExportService(db)
    return StreamingResponse(
        service.export_habits(current_user.id),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=habits.csv"},
    )


@router.get("/skills")
async def export_skills(current_user: CurrentUser, db: DB):
    service = ExportService(db)
    return StreamingResponse(
        service.export_skills(current_user.id),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=skills.csv"},
    )


@router.get("/backup")
async def export_backup(current_user: CurrentUser, db: DB):
    service = ExportService(db)
    data = await service.export_all_json(current_user.id)
    return JSONResponse(
        content=data,
        headers={"Content-Disposition": "attachment; filename=trainer-backup.json"},
    )


@router.post("/ical-token")
async def generate_ical_token(current_user: CurrentUser, db: DB):
    token = str(uuid.uuid4())
    prefs = dict(current_user.preferences or {})
    prefs["ical_token"] = token
    current_user.preferences = prefs
    await db.flush()
    return {"ical_token": token}


# Public endpoint — no auth header, token in URL
@router.get("/ical/{feed_token}.ics")
async def get_ical_feed(feed_token: str, db: DB):
    result = await db.execute(select(User))
    users = result.scalars().all()

    target_user = None
    for user in users:
        if user.preferences and user.preferences.get("ical_token") == feed_token:
            target_user = user
            break

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid feed token"
        )

    ical_content = await generate_ical_feed(db, target_user.id)
    return Response(
        content=ical_content,
        media_type="text/calendar",
        headers={"Content-Disposition": "inline; filename=trainer.ics"},
    )
