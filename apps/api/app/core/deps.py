"""FastAPI dependencies: current user, permissions, branch scope."""

from collections.abc import Callable
from dataclasses import dataclass

import jwt
from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core import errors
from app.core.config import settings
from app.core.rbac import role_has_permission
from app.core.security import decode_token
from app.db.base import get_db as get_db
from app.modules.users_roles.models import User

ALL_BRANCHES = "*"


@dataclass
class TokenUser:
    """The authenticated user, as carried by the access token + DB row."""

    id: str
    email: str
    role: str
    branch_id: str | None
    branches: list[str]
    db_user: User


def _bearer_token(request: Request) -> str:
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        raise errors.ApiError(401, errors.UNAUTHORIZED, "Missing or invalid Authorization header.")
    return header[len("Bearer ") :].strip()


def get_current_user(request: Request, db: Session = Depends(get_db)) -> TokenUser:
    """Decode the access token, load the user, block inactive accounts."""
    token = _bearer_token(request)
    try:
        payload = decode_token(token, "access")
    except jwt.ExpiredSignatureError:
        raise errors.ApiError(401, errors.TOKEN_EXPIRED, "Access token has expired.") from None
    except jwt.PyJWTError:
        raise errors.ApiError(401, errors.TOKEN_INVALID, "Access token is invalid.") from None
    user_id = payload.get("sub")
    if not isinstance(user_id, str):
        raise errors.ApiError(401, errors.TOKEN_INVALID, "Access token is invalid.")
    user = db.get(User, user_id)
    if user is None or user.deleted_at is not None:
        raise errors.ApiError(401, errors.UNAUTHORIZED, "User no longer exists.")
    if not user.is_active:
        raise errors.ApiError(403, errors.ACCOUNT_INACTIVE, "User account is inactive.")
    role = user.role
    role_name = role.name if role is not None else ""
    branch_ids = [ub.branch_id for ub in user.branches]
    token_branches = payload.get("branches")
    branches = branch_ids if isinstance(token_branches, list) else branch_ids
    branch_id = payload.get("branch_id")
    return TokenUser(
        id=user.id,
        email=user.email,
        role=role_name,
        branch_id=branch_id if isinstance(branch_id, str) else None,
        branches=[str(b) for b in branches],
        db_user=user,
    )


def require_permission(permission: str) -> Callable[[TokenUser], TokenUser]:
    """Dependency factory: 403 unless the user's role has the permission."""

    def _check(user: TokenUser = Depends(get_current_user)) -> TokenUser:
        if not role_has_permission(user.role, permission):
            raise errors.ApiError(
                403,
                errors.FORBIDDEN,
                f"Role '{user.role}' may not perform '{permission}'.",
            )
        return user

    return _check


def branch_scope(user: TokenUser) -> list[str] | str:
    """Branch ids the user may access, or ALL_BRANCHES for Super Admin."""
    if user.role == "Super Admin":
        return ALL_BRANCHES
    return list(user.branches)


def assert_branch_in_scope(user: TokenUser, branch_id: str | None) -> None:
    """403 if the branch is outside the user's scope (Super Admin: any)."""
    scope = branch_scope(user)
    if scope == ALL_BRANCHES:
        return
    if branch_id is None or branch_id not in scope:
        raise errors.ApiError(403, errors.FORBIDDEN, "Branch is outside your assigned branches.")


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client is not None else "unknown"


def is_testing() -> bool:
    return settings.testing
