from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.habits.models import ActivityLog
from src.modules.integrations.models import UserIntegration
from src.modules.integrations.schemas import IntegrationStatus, StravaSyncResult
from src.modules.integrations.strava import (
    ensure_valid_token,
    exchange_code,
    get_activities,
)


class IntegrationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def connect_strava(self, user_id: UUID, code: str) -> UserIntegration:
        tokens = await exchange_code(code)

        # Upsert
        result = await self.db.execute(
            select(UserIntegration).where(
                UserIntegration.user_id == user_id,
                UserIntegration.provider == "strava",
            )
        )
        integration = result.scalar_one_or_none()

        if integration:
            integration.access_token = tokens["access_token"]
            integration.refresh_token = tokens["refresh_token"]
            integration.expires_at = datetime.fromtimestamp(
                tokens["expires_at"], tz=timezone.utc
            )
            integration.provider_user_id = str(tokens.get("athlete", {}).get("id", ""))
            integration.scopes = "activity:read_all"
        else:
            integration = UserIntegration(
                user_id=user_id,
                provider="strava",
                access_token=tokens["access_token"],
                refresh_token=tokens["refresh_token"],
                expires_at=datetime.fromtimestamp(
                    tokens["expires_at"], tz=timezone.utc
                ),
                provider_user_id=str(tokens.get("athlete", {}).get("id", "")),
                scopes="activity:read_all",
            )
            self.db.add(integration)

        await self.db.flush()
        return integration

    async def disconnect_strava(self, user_id: UUID) -> None:
        result = await self.db.execute(
            select(UserIntegration).where(
                UserIntegration.user_id == user_id,
                UserIntegration.provider == "strava",
            )
        )
        integration = result.scalar_one_or_none()
        if integration:
            await self.db.delete(integration)
            await self.db.flush()

    async def get_integration_status(
        self, user_id: UUID, provider: str
    ) -> IntegrationStatus:
        result = await self.db.execute(
            select(UserIntegration).where(
                UserIntegration.user_id == user_id,
                UserIntegration.provider == provider,
            )
        )
        integration = result.scalar_one_or_none()

        if integration:
            return IntegrationStatus(
                provider=provider,
                connected=True,
                provider_user_id=integration.provider_user_id,
                connected_at=integration.created_at,
            )
        return IntegrationStatus(provider=provider, connected=False)

    async def sync_strava_activities(self, user_id: UUID) -> StravaSyncResult:
        result = await self.db.execute(
            select(UserIntegration).where(
                UserIntegration.user_id == user_id,
                UserIntegration.provider == "strava",
            )
        )
        integration = result.scalar_one_or_none()
        if not integration:
            return StravaSyncResult(imported_count=0, skipped_count=0)

        access_token = await ensure_valid_token(integration)
        await self.db.flush()

        # Get last sync timestamp from metadata
        last_sync = integration.metadata_.get("last_sync_epoch")
        activities = await get_activities(access_token, after=last_sync)

        # Get existing strava activity IDs to dedup
        existing_result = await self.db.execute(
            select(ActivityLog.notes).where(
                ActivityLog.user_id == user_id,
                ActivityLog.domain == "fitness",
                ActivityLog.notes.like("strava:%"),
            )
        )
        existing_ids = {row[0] for row in existing_result.all()}

        imported = 0
        skipped = 0

        for activity in activities:
            strava_id = f"strava:{activity['id']}"
            if strava_id in existing_ids:
                skipped += 1
                continue

            started = datetime.fromisoformat(
                activity["start_date"].replace("Z", "+00:00")
            )
            duration = activity.get("elapsed_time", 0)

            log = ActivityLog(
                user_id=user_id,
                domain="fitness",
                started_at=started,
                duration_seconds=duration,
                notes=strava_id,
            )
            self.db.add(log)
            imported += 1

        # Update last sync time
        meta = dict(integration.metadata_ or {})
        meta["last_sync_epoch"] = int(datetime.now(timezone.utc).timestamp())
        integration.metadata_ = meta
        await self.db.flush()

        return StravaSyncResult(imported_count=imported, skipped_count=skipped)
