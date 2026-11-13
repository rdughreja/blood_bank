"""Audit log service — read-only listing with filters and branch scoping."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.deps import ALL_BRANCHES, TokenUser, branch_scope
from app.modules.audit.models import AuditLog


def list_audit_logs(
    db: Session,
    user: TokenUser,
    page: int,
    page_size: int,
    entity: str | None = None,
    action: str | None = None,
    user_id: str | None = None,
    branch_id: str | None = None,
) -> tuple[list[AuditLog], int]:
    query = select(AuditLog)
    scope = branch_scope(user)
    # Viewer / Auditor may read the audit trail across all branches.
    if scope != ALL_BRANCHES and user.role != "Viewer / Auditor":
        query = query.where(AuditLog.branch_id.in_(scope))
    if entity:
        query = query.where(AuditLog.entity == entity)
    if action:
        query = query.where(AuditLog.action == action)
    if user_id:
        query = query.where(AuditLog.user_id == user_id)
    if branch_id:
        query = query.where(AuditLog.branch_id == branch_id)
    total = db.execute(select(func.count()).select_from(query.subquery())).scalar_one()
    rows = (
        db.execute(
            query.order_by(AuditLog.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        .scalars()
        .all()
    )
    return list(rows), int(total)
