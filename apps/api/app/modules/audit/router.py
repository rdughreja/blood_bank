"""Audit log router — GET /audit-logs (Admin/Auditor only)."""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.deps import TokenUser, get_db, require_permission
from app.core.envelope import (
    SuccessEnvelope,
    make_page_meta,
    paginate_params,
)
from app.modules.audit import service
from app.modules.audit.schemas import AuditOut

router = APIRouter(prefix="/audit-logs", tags=["audit"])


def _to_out(row: object) -> AuditOut:
    from app.modules.audit.models import AuditLog

    assert isinstance(row, AuditLog)
    return AuditOut(
        id=row.id,
        user_id=row.user_id,
        user_email=row.user_email,
        action=row.action,
        entity=row.entity,
        entity_id=row.entity_id,
        old_value=row.old_value,
        new_value=row.new_value,
        ip_address=row.ip_address,
        branch_id=row.branch_id,
        created_at=row.created_at,
    )


@router.get("", response_model=SuccessEnvelope[list[AuditOut]])
def list_audit_logs(
    request: Request,
    page: int = 1,
    page_size: int = Query(default=20, alias="pageSize"),
    entity: str | None = None,
    action: str | None = None,
    user_id: str | None = None,
    branch_id: str | None = None,
    user: TokenUser = Depends(require_permission("audit:read")),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    page, page_size = paginate_params(page, page_size)
    rows, total = service.list_audit_logs(
        db, user, page, page_size, entity, action, user_id, branch_id
    )
    return {
        "success": True,
        "data": [_to_out(r) for r in rows],
        "meta": make_page_meta(request.state.request_id, page, page_size, total),
    }
