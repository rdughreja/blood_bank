"""Master data service — CRUD per type, global + branch-scoped masters."""

from datetime import UTC

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.core import errors
from app.core.audit import write_audit
from app.core.deps import ALL_BRANCHES, TokenUser, branch_scope
from app.modules.masters.models import MASTER_TYPES, MasterData
from app.modules.masters.schemas import MasterCreate, MasterUpdate


def _visible_query(db: Session, user: TokenUser, master_type: str) -> Select[MasterData]:
    query = select(MasterData).where(
        MasterData.type == master_type, MasterData.deleted_at.is_(None)
    )
    scope = branch_scope(user)
    if scope != ALL_BRANCHES:
        # Global masters (branch_id null) plus the user's own branches.
        query = query.where((MasterData.branch_id.is_(None)) | (MasterData.branch_id.in_(scope)))
    return query.order_by(MasterData.code)


def list_masters(
    db: Session, user: TokenUser, master_type: str, page: int, page_size: int
) -> tuple[list[MasterData], int]:
    if master_type not in MASTER_TYPES:
        raise errors.ApiError(404, errors.NOT_FOUND, f"Unknown master type '{master_type}'.")
    query = _visible_query(db, user, master_type)
    total = db.execute(select(func.count()).select_from(query.subquery())).scalar_one()
    rows = db.execute(query.offset((page - 1) * page_size).limit(page_size)).scalars().all()
    return list(rows), int(total)


def create_master(
    db: Session, user: TokenUser, master_type: str, payload: MasterCreate, ip: str | None
) -> MasterData:
    if master_type not in MASTER_TYPES:
        raise errors.ApiError(404, errors.NOT_FOUND, f"Unknown master type '{master_type}'.")
    branch_id = payload.branch_id
    if branch_id is None:
        if user.role != "Super Admin":
            raise errors.ApiError(
                403, errors.FORBIDDEN, "Only Super Admin may create global masters."
            )
    else:
        scope = branch_scope(user)
        if scope != ALL_BRANCHES and branch_id not in scope:
            raise errors.ApiError(
                403, errors.FORBIDDEN, "Cannot create a master for another branch."
            )
    existing = db.execute(
        select(MasterData).where(
            MasterData.type == master_type,
            MasterData.code == payload.code,
            MasterData.branch_id == branch_id,
            MasterData.deleted_at.is_(None),
        )
    ).scalar_one_or_none()
    if existing is not None:
        raise errors.ApiError(409, errors.CONFLICT, f"Master code '{payload.code}' already exists.")
    row = MasterData(
        type=master_type,
        code=payload.code,
        name=payload.name,
        extra=payload.extra,
        branch_id=branch_id,
        created_by=user.id,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    write_audit(
        db,
        user,
        "create",
        "MasterData",
        row.id,
        None,
        {"type": master_type, "code": payload.code},
        ip,
        branch_id,
    )
    db.commit()
    return row


def update_master(
    db: Session, user: TokenUser, master_id: str, payload: MasterUpdate, ip: str | None
) -> MasterData:
    row = db.get(MasterData, master_id)
    if row is None or row.deleted_at is not None:
        raise errors.ApiError(404, errors.NOT_FOUND, "Master record not found.")
    scope = branch_scope(user)
    if scope != ALL_BRANCHES:
        if row.branch_id is None:
            raise errors.ApiError(404, errors.NOT_FOUND, "Master record not found.")
        if row.branch_id not in scope:
            raise errors.ApiError(404, errors.NOT_FOUND, "Master record not found.")
    old = {"name": row.name}
    if payload.name is not None:
        row.name = payload.name
    if payload.extra is not None:
        row.extra = payload.extra
    if payload.is_active is not None:
        row.is_active = payload.is_active
    db.commit()
    db.refresh(row)
    write_audit(
        db, user, "update", "MasterData", row.id, old, {"name": row.name}, ip, row.branch_id
    )
    db.commit()
    return row


def delete_master(
    db: Session, user: TokenUser, master_id: str, reason: str, ip: str | None
) -> MasterData:
    """Soft delete only — never a hard delete."""
    from datetime import datetime

    row = db.get(MasterData, master_id)
    if row is None or row.deleted_at is not None:
        raise errors.ApiError(404, errors.NOT_FOUND, "Master record not found.")
    scope = branch_scope(user)
    if scope != ALL_BRANCHES and (row.branch_id is None or row.branch_id not in scope):
        raise errors.ApiError(404, errors.NOT_FOUND, "Master record not found.")
    row.deleted_at = datetime.now(UTC)
    row.delete_reason = reason
    row.is_active = False
    db.commit()
    db.refresh(row)
    write_audit(
        db, user, "delete", "MasterData", row.id, None, {"reason": reason}, ip, row.branch_id
    )
    db.commit()
    return row
