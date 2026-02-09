from datetime import datetime

from pydantic import BaseModel


class IntegrationStatus(BaseModel):
    provider: str
    connected: bool
    provider_user_id: str | None = None
    connected_at: datetime | None = None


class StravaSyncResult(BaseModel):
    imported_count: int
    skipped_count: int
