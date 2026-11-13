"""Settings service — key-value, per branch with global fallback."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import errors
from app.core.audit import write_audit
from app.core.deps import TokenUser, assert_branch_in_scope, branch_scope
from app.modules.settings.models import Setting
from app.modules.settings.schemas import SettingUpsert


def get_effective_value(db: Session, key: str, branch_id: str | None) -> Any | None:
    """Branch value wins; otherwise the global value; otherwise None."""
    if branch_id is not None:
        row = db.execute(
            select(Setting).where(
                Setting.key == key,
                Setting.scope == "branch",
                Setting.branch_id == branch_id,
                Setting.deleted_at.is_(None),
            )
        ).scalar_one_or_none()
        if row is not None:
            return row.value
    row = db.execute(
        select(Setting).where(
            Setting.key == key,
            Setting.scope == "global",
            Setting.deleted_at.is_(None),
        )
    ).scalar_one_or_none()
    return row.value if row is not None else None


def get_value(db: Session, key: str, branch_id: str | None, default: Any) -> Any:
    value = get_effective_value(db, key, branch_id)
    return default if value is None else value


def list_effective(db: Session, branch_id: str | None) -> list[Setting]:
    """All settings merged: global rows overridden by branch rows of same key."""
    rows = (
        db.execute(select(Setting).where(Setting.deleted_at.is_(None)).order_by(Setting.key))
        .scalars()
        .all()
    )
    merged: dict[str, Setting] = {}
    for row in rows:
        if row.scope == "global":
            merged.setdefault(row.key, row)
        elif row.scope == "branch" and row.branch_id == branch_id:
            merged[row.key] = row
    return list(merged.values())


def upsert_setting(db: Session, user: TokenUser, payload: SettingUpsert, ip: str | None) -> Setting:
    """Upsert a setting. Global scope is Super Admin only; branch scope must
    be inside the caller's branches."""
    if payload.scope == "global":
        if user.role != "Super Admin":
            raise errors.ApiError(
                403, errors.FORBIDDEN, "Only Super Admin may change global settings."
            )
        branch_id = None
    else:
        if not payload.branch_id:
            raise errors.ApiError(
                400, errors.VALIDATION_ERROR, "branch_id is required for branch settings."
            )
        assert_branch_in_scope(user, payload.branch_id)
        branch_id = payload.branch_id
    existing = db.execute(
        select(Setting).where(
            Setting.key == payload.key,
            Setting.scope == payload.scope,
            Setting.branch_id == branch_id,
            Setting.deleted_at.is_(None),
        )
    ).scalar_one_or_none()
    if existing is not None:
        old = {"value": existing.value}
        existing.value = payload.value
        if payload.label is not None:
            existing.label = payload.label
        if payload.description is not None:
            existing.description = payload.description
        existing.confirm_with_mo = payload.confirm_with_mo
        write_audit(
            db,
            user,
            "update",
            "Setting",
            existing.id,
            old,
            {"value": payload.value},
            ip,
            branch_id,
        )
        db.commit()
        db.refresh(existing)
        return existing
    row = Setting(
        key=payload.key,
        value=payload.value,
        scope=payload.scope,
        branch_id=branch_id,
        confirm_with_mo=payload.confirm_with_mo,
        label=payload.label,
        description=payload.description,
        created_by=user.id,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    write_audit(
        db, user, "create", "Setting", row.id, None, {"value": payload.value}, ip, branch_id
    )
    db.commit()
    return row


def visible_branches_for_settings(user: TokenUser) -> list[str] | str:
    return branch_scope(user)
