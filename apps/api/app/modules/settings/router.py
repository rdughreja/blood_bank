"""Settings router — GET /settings, PUT /settings."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.deps import TokenUser, get_client_ip, get_db, require_permission
from app.core.envelope import SuccessEnvelope, make_meta
from app.modules.settings import service
from app.modules.settings.schemas import SettingOut, SettingUpsert

router = APIRouter(prefix="/settings", tags=["settings"])


def _to_out(row: object) -> SettingOut:
    from app.modules.settings.models import Setting

    assert isinstance(row, Setting)
    return SettingOut(
        id=row.id,
        key=row.key,
        value=row.value,
        scope=row.scope,
        branch_id=row.branch_id,
        confirm_with_mo=row.confirm_with_mo,
        label=row.label,
        description=row.description,
    )


@router.get("", response_model=SuccessEnvelope[list[SettingOut]])
def list_settings(
    request: Request,
    branch_id: str | None = None,
    user: TokenUser = Depends(require_permission("settings:read")),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    """Effective settings for a branch (branch values override globals)."""
    effective_branch = branch_id or user.branch_id
    rows = service.list_effective(db, effective_branch)
    return {
        "success": True,
        "data": [_to_out(r) for r in rows],
        "meta": make_meta(request.state.request_id),
    }


@router.put("", response_model=SuccessEnvelope[SettingOut])
def upsert_setting(
    request: Request,
    payload: SettingUpsert,
    user: TokenUser = Depends(require_permission("settings:update")),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    row = service.upsert_setting(db, user, payload, get_client_ip(request))
    return {"success": True, "data": _to_out(row), "meta": make_meta(request.state.request_id)}
