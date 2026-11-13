"""User / role service — CRUD with branch scoping and soft delete."""

from datetime import UTC
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core import errors
from app.core.audit import write_audit
from app.core.crypto import blind_index
from app.core.deps import ALL_BRANCHES, TokenUser, branch_scope
from app.core.rbac import ROLE_SUPER_ADMIN
from app.core.security import hash_password, validate_password_policy, verify_password
from app.modules.branches.models import Branch
from app.modules.users_roles.models import Permission, Role, RolePermission, User, UserBranch
from app.modules.users_roles.schemas import UserCreate, UserUpdate


def _branches_out(db: Session, user: User) -> list[dict[str, str]]:
    rows = (
        db.execute(
            select(Branch)
            .join(UserBranch, UserBranch.branch_id == Branch.id)
            .where(UserBranch.user_id == user.id, Branch.deleted_at.is_(None))
            .order_by(Branch.code)
        )
        .scalars()
        .all()
    )
    return [{"id": b.id, "code": b.code, "name": b.name} for b in rows]


def _visible_user_ids(db: Session, caller: TokenUser) -> set[str] | None:
    """User ids the caller may see; None = all (Super Admin)."""
    scope = branch_scope(caller)
    if scope == ALL_BRANCHES:
        return None
    rows = (
        db.execute(select(UserBranch.user_id).where(UserBranch.branch_id.in_(scope)))
        .scalars()
        .all()
    )
    ids = set(rows)
    ids.add(caller.id)  # a user can always see themselves
    return ids


def list_users(db: Session, caller: TokenUser, page: int, page_size: int) -> tuple[list[User], int]:
    visible = _visible_user_ids(db, caller)
    query = select(User).where(User.deleted_at.is_(None))
    if visible is not None:
        query = query.where(User.id.in_(visible))
    total = db.execute(select(func.count()).select_from(query.subquery())).scalar_one()
    rows = (
        db.execute(query.order_by(User.full_name).offset((page - 1) * page_size).limit(page_size))
        .scalars()
        .all()
    )
    return list(rows), int(total)


def get_user(db: Session, caller: TokenUser, user_id: str) -> User:
    row = db.get(User, user_id)
    if row is None or row.deleted_at is not None:
        raise errors.ApiError(404, errors.NOT_FOUND, "User not found.")
    visible = _visible_user_ids(db, caller)
    if visible is not None and row.id not in visible:
        raise errors.ApiError(404, errors.NOT_FOUND, "User not found.")
    return row


def _check_branch_assignment(db: Session, caller: TokenUser, branch_ids: list[str]) -> None:
    scope = branch_scope(caller)
    if scope != ALL_BRANCHES:
        for branch_id in branch_ids:
            if branch_id not in scope:
                raise errors.ApiError(
                    403, errors.FORBIDDEN, "Cannot assign a user to a branch outside your scope."
                )
    for branch_id in branch_ids:
        branch = db.get(Branch, branch_id)
        if branch is None or branch.deleted_at is not None:
            raise errors.ApiError(404, errors.NOT_FOUND, f"Branch {branch_id} not found.")


def create_user(db: Session, caller: TokenUser, payload: UserCreate, ip: str | None) -> User:
    violations = validate_password_policy(payload.password)
    if violations:
        raise errors.ApiError(
            400,
            errors.VALIDATION_ERROR,
            "Password does not meet the policy.",
            {"violations": violations},
        )
    existing = db.execute(
        select(User).where(User.email_lookup == blind_index(payload.email))
    ).scalar_one_or_none()
    if existing is not None:
        raise errors.ApiError(409, errors.CONFLICT, "A user with this email already exists.")
    role = db.get(Role, payload.role_id)
    if role is None:
        raise errors.ApiError(404, errors.NOT_FOUND, "Role not found.")
    if role.name == ROLE_SUPER_ADMIN and caller.role != ROLE_SUPER_ADMIN:
        raise errors.ApiError(403, errors.FORBIDDEN, "Only Super Admin may create Super Admins.")
    _check_branch_assignment(db, caller, payload.branch_ids)
    primary = payload.primary_branch_id or (payload.branch_ids[0] if payload.branch_ids else None)
    if primary is not None and primary not in payload.branch_ids:
        raise errors.ApiError(400, errors.VALIDATION_ERROR, "Primary branch must be assigned.")
    row = User(
        email=payload.email,
        email_lookup=blind_index(payload.email),
        mobile=payload.mobile,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
        role_id=role.id,
        created_by=caller.id,
    )
    db.add(row)
    db.flush()
    for branch_id in payload.branch_ids:
        db.add(UserBranch(user_id=row.id, branch_id=branch_id, is_primary=(branch_id == primary)))
    db.commit()
    db.refresh(row)
    write_audit(db, caller, "create", "User", row.id, None, {"email": payload.email}, ip, primary)
    db.commit()
    return row


def update_user(
    db: Session, caller: TokenUser, user_id: str, payload: UserUpdate, ip: str | None
) -> User:
    row = get_user(db, caller, user_id)
    if row.id == caller.id and payload.is_active is False:
        raise errors.ApiError(400, errors.VALIDATION_ERROR, "You cannot deactivate yourself.")
    old = {"full_name": row.full_name, "is_active": row.is_active}
    if payload.full_name is not None:
        row.full_name = payload.full_name
    if payload.mobile is not None:
        row.mobile = payload.mobile
    if payload.role_id is not None:
        role = db.get(Role, payload.role_id)
        if role is None:
            raise errors.ApiError(404, errors.NOT_FOUND, "Role not found.")
        if role.name == ROLE_SUPER_ADMIN and caller.role != ROLE_SUPER_ADMIN:
            raise errors.ApiError(403, errors.FORBIDDEN, "Only Super Admin may assign Super Admin.")
        row.role_id = role.id
    if payload.branch_ids is not None:
        _check_branch_assignment(db, caller, payload.branch_ids)
        for ub in list(row.branches):
            db.delete(ub)
        primary = payload.primary_branch_id or (
            payload.branch_ids[0] if payload.branch_ids else None
        )
        for branch_id in payload.branch_ids:
            db.add(
                UserBranch(user_id=row.id, branch_id=branch_id, is_primary=(branch_id == primary))
            )
    if payload.is_active is not None:
        row.is_active = payload.is_active
    db.commit()
    db.refresh(row)
    write_audit(
        db,
        caller,
        "update",
        "User",
        row.id,
        old,
        {"full_name": row.full_name, "is_active": row.is_active},
        ip,
        None,
    )
    db.commit()
    return row


def delete_user(db: Session, caller: TokenUser, user_id: str, reason: str, ip: str | None) -> User:
    """Soft delete only — never a hard delete."""
    from datetime import datetime

    row = get_user(db, caller, user_id)
    if row.id == caller.id:
        raise errors.ApiError(400, errors.VALIDATION_ERROR, "You cannot delete yourself.")
    row.deleted_at = datetime.now(UTC)
    row.delete_reason = reason
    row.is_active = False
    db.commit()
    db.refresh(row)
    write_audit(db, caller, "delete", "User", row.id, None, {"reason": reason}, ip, None)
    db.commit()
    return row


def reset_password(
    db: Session, caller: TokenUser, user_id: str, new_password: str, ip: str | None
) -> User:
    violations = validate_password_policy(new_password)
    if violations:
        raise errors.ApiError(
            400,
            errors.VALIDATION_ERROR,
            "Password does not meet the policy.",
            {"violations": violations},
        )
    row = get_user(db, caller, user_id)
    row.password_hash = hash_password(new_password)
    row.failed_login_attempts = 0
    row.locked_until = None
    db.commit()
    write_audit(db, caller, "password_reset", "User", row.id, None, None, ip, None)
    db.commit()
    return row


def change_own_password(
    db: Session, caller: TokenUser, current_password: str, new_password: str
) -> None:
    violations = validate_password_policy(new_password)
    if violations:
        raise errors.ApiError(
            400,
            errors.VALIDATION_ERROR,
            "Password does not meet the policy.",
            {"violations": violations},
        )
    row = db.get(User, caller.id)
    if row is None or not verify_password(current_password, row.password_hash):
        raise errors.ApiError(401, errors.INVALID_CREDENTIALS, "Current password is incorrect.")
    row.password_hash = hash_password(new_password)
    db.commit()


def list_roles(db: Session) -> list[dict[str, Any]]:
    roles = db.execute(select(Role).order_by(Role.name)).scalars().all()
    out: list[dict[str, Any]] = []
    for role in roles:
        perm_rows = (
            db.execute(
                select(Permission.name)
                .join(RolePermission, RolePermission.permission_id == Permission.id)
                .where(RolePermission.role_id == role.id)
                .order_by(Permission.name)
            )
            .scalars()
            .all()
        )
        out.append(
            {
                "id": role.id,
                "name": role.name,
                "description": role.description,
                "permissions": list(perm_rows),
            }
        )
    return out
