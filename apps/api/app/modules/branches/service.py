"""Branch service — CRUD with branch scoping and soft delete."""

from datetime import UTC

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.core import errors
from app.core.audit import write_audit
from app.core.deps import ALL_BRANCHES, TokenUser, branch_scope
from app.modules.branches.models import Branch
from app.modules.branches.schemas import BranchCreate, BranchUpdate


def _visible_query(db: Session, user: TokenUser) -> Select[Branch]:
    query = select(Branch).where(Branch.deleted_at.is_(None))
    scope = branch_scope(user)
    if scope != ALL_BRANCHES:
        query = query.where(Branch.id.in_(scope))
    return query.order_by(Branch.code)


def list_branches(
    db: Session, user: TokenUser, page: int, page_size: int
) -> tuple[list[Branch], int]:
    total = db.execute(
        select(func.count()).select_from(_visible_query(db, user).subquery())
    ).scalar_one()
    rows = (
        db.execute(_visible_query(db, user).offset((page - 1) * page_size).limit(page_size))
        .scalars()
        .all()
    )
    return list(rows), int(total)


def get_branch(db: Session, user: TokenUser, branch_id: str) -> Branch:
    """404 if the branch does not exist in the caller's scope — never reveal
    that another branch's record exists."""
    row = db.execute(
        select(Branch).where(Branch.id == branch_id, Branch.deleted_at.is_(None))
    ).scalar_one_or_none()
    if row is None:
        raise errors.ApiError(404, errors.NOT_FOUND, "Branch not found.")
    scope = branch_scope(user)
    if scope != ALL_BRANCHES and row.id not in scope:
        raise errors.ApiError(404, errors.NOT_FOUND, "Branch not found.")
    return row


def create_branch(db: Session, user: TokenUser, payload: BranchCreate, ip: str | None) -> Branch:
    existing = db.execute(
        select(Branch).where(Branch.code == payload.code, Branch.deleted_at.is_(None))
    ).scalar_one_or_none()
    if existing is not None:
        raise errors.ApiError(409, errors.CONFLICT, f"Branch code '{payload.code}' exists.")
    row = Branch(
        code=payload.code,
        name=payload.name,
        address=payload.address,
        licence_no=payload.licence_no,
        is_storage_centre=payload.is_storage_centre,
        created_by=user.id,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    write_audit(db, user, "create", "Branch", row.id, None, {"code": row.code}, ip, row.id)
    db.commit()
    return row


def update_branch(
    db: Session, user: TokenUser, branch_id: str, payload: BranchUpdate, ip: str | None
) -> Branch:
    row = get_branch(db, user, branch_id)
    old = {"name": row.name, "is_storage_centre": row.is_storage_centre}
    if payload.name is not None:
        row.name = payload.name
    if payload.address is not None:
        row.address = payload.address
    if payload.licence_no is not None:
        row.licence_no = payload.licence_no
    if payload.is_storage_centre is not None:
        row.is_storage_centre = payload.is_storage_centre
    if payload.is_active is not None:
        row.is_active = payload.is_active
    db.commit()
    db.refresh(row)
    write_audit(
        db,
        user,
        "update",
        "Branch",
        row.id,
        old,
        {"name": row.name, "is_storage_centre": row.is_storage_centre},
        ip,
        row.id,
    )
    db.commit()
    return row


def delete_branch(
    db: Session, user: TokenUser, branch_id: str, reason: str, ip: str | None
) -> Branch:
    """Soft delete only — never a hard delete."""
    from datetime import datetime

    row = get_branch(db, user, branch_id)
    row.deleted_at = datetime.now(UTC)
    row.delete_reason = reason
    row.is_active = False
    db.commit()
    db.refresh(row)
    write_audit(db, user, "delete", "Branch", row.id, None, {"reason": reason}, ip, row.id)
    db.commit()
    return row
