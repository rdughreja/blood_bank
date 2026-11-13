"""Audit log schemas."""

from typing import Any

from pydantic import BaseModel

from app.core.envelope import UtcDateTime


class AuditOut(BaseModel):
    id: str
    user_id: str | None
    user_email: str | None
    action: str
    entity: str
    entity_id: str | None
    old_value: dict[str, Any] | None
    new_value: dict[str, Any] | None
    ip_address: str | None
    branch_id: str | None
    created_at: UtcDateTime
