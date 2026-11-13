"""Audit log helper — called by services on create/update/soft-delete."""

from typing import Any

from sqlalchemy.orm import Session

from app.core.deps import TokenUser
from app.modules.audit.models import AuditLog


def write_audit(
    db: Session,
    user: TokenUser | None,
    action: str,
    entity: str,
    entity_id: str | None,
    old_value: dict[str, Any] | None,
    new_value: dict[str, Any] | None,
    ip_address: str | None,
    branch_id: str | None,
) -> AuditLog:
    entry = AuditLog(
        user_id=user.id if user else None,
        user_email=user.email if user else None,
        action=action,
        entity=entity,
        entity_id=entity_id,
        old_value=old_value,
        new_value=new_value,
        ip_address=ip_address,
        branch_id=branch_id,
    )
    db.add(entry)
    return entry
