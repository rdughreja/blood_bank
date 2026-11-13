"""Auth service — login, refresh (rotating), logout, MFA (TOTP), branch switch."""

from datetime import UTC, datetime, timedelta

import jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import errors
from app.core.audit import write_audit
from app.core.config import settings
from app.core.crypto import blind_index
from app.core.deps import TokenUser
from app.core.rbac import role_requires_mfa
from app.core.security import (
    create_access_token,
    create_mfa_token,
    create_refresh_token,
    decode_token,
    generate_totp_secret,
    hash_password,
    hash_token,
    totp_provisioning_uri,
    verify_password,
    verify_totp,
)
from app.modules.auth.models import RefreshToken
from app.modules.settings.service import get_value
from app.modules.users_roles.models import User

LOCKOUT_THRESHOLD_KEY = "security.lockout_threshold"
LOCKOUT_MINUTES_KEY = "security.lockout_minutes"
DEFAULT_LOCKOUT_THRESHOLD = 5
DEFAULT_LOCKOUT_MINUTES = 15


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _branches_for(user: User) -> list[str]:
    return [ub.branch_id for ub in user.branches]


def _primary_branch(user: User) -> str | None:
    for ub in user.branches:
        if ub.is_primary:
            return ub.branch_id
    branches = _branches_for(user)
    return branches[0] if branches else None


def _issue_tokens(db: Session, user: User) -> tuple[str, str]:
    """Create a refresh-token row and return (access_token, refresh_token)."""
    role_name = user.role.name if user.role is not None else ""
    branches = _branches_for(user)
    access = create_access_token(
        user_id=user.id,
        email=user.email,
        role=role_name,
        branch_id=_primary_branch(user),
        branches=branches,
    )
    refresh, jti = create_refresh_token(user.id)
    row = RefreshToken(
        user_id=user.id,
        token_hash=hash_token(jti),
        expires_at=_utcnow() + timedelta(days=settings.refresh_token_expire_days),
        created_by=user.id,
    )
    db.add(row)
    db.commit()
    return access, refresh


def _find_user_by_email(db: Session, email: str) -> User | None:
    return db.execute(
        select(User).where(User.email_lookup == blind_index(email), User.deleted_at.is_(None))
    ).scalar_one_or_none()


def login(db: Session, email: str, password: str, ip: str | None) -> dict[str, object]:
    """Authenticate. Returns tokens, or an MFA challenge for MFA roles."""
    user = _find_user_by_email(db, email)
    if user is None:
        raise errors.ApiError(401, errors.INVALID_CREDENTIALS, "Invalid email or password.")
    if not user.is_active:
        raise errors.ApiError(403, errors.ACCOUNT_INACTIVE, "User account is inactive.")
    if user.locked_until is not None and user.locked_until > _utcnow():
        raise errors.ApiError(
            403,
            errors.ACCOUNT_LOCKED,
            "Account is locked after too many failed attempts. Try again later.",
            {"lockedUntil": user.locked_until.isoformat()},
        )
    if not verify_password(password, user.password_hash):
        threshold = int(get_value(db, LOCKOUT_THRESHOLD_KEY, None, DEFAULT_LOCKOUT_THRESHOLD))
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= threshold:
            minutes = int(get_value(db, LOCKOUT_MINUTES_KEY, None, DEFAULT_LOCKOUT_MINUTES))
            user.locked_until = _utcnow() + timedelta(minutes=minutes)
            db.commit()
            write_audit(
                db,
                None,
                "login_failed_lockout",
                "User",
                user.id,
                None,
                {"failedAttempts": user.failed_login_attempts},
                ip,
                None,
            )
            db.commit()
            raise errors.ApiError(
                403,
                errors.ACCOUNT_LOCKED,
                "Account locked after too many failed login attempts.",
            )
        db.commit()
        raise errors.ApiError(
            401,
            errors.INVALID_CREDENTIALS,
            "Invalid email or password.",
            {"attemptsRemaining": threshold - user.failed_login_attempts},
        )
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login_at = _utcnow()
    db.commit()
    role_name = user.role.name if user.role is not None else ""
    write_audit(db, None, "login", "User", user.id, None, {"email": email}, ip, None)
    db.commit()
    if role_requires_mfa(role_name):
        mfa_token = create_mfa_token(user.id)
        return {
            "mfa_required": True,
            "mfa_setup_required": not user.mfa_enabled,
            "mfa_token": mfa_token,
        }
    access, refresh = _issue_tokens(db, user)
    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer",
        "mfa_required": False,
    }


def _revoke_refresh_row(db: Session, jti: str, replaced_by: str | None) -> None:
    row = db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == hash_token(jti))
    ).scalar_one_or_none()
    if row is not None and row.revoked_at is None:
        row.revoked_at = _utcnow()
        row.replaced_by = replaced_by
        db.commit()


def refresh_tokens(db: Session, refresh_token: str) -> tuple[str, str]:
    """Rotate: revoke the old refresh token, issue a new pair."""
    try:
        payload = decode_token(refresh_token, "refresh")
    except jwt.ExpiredSignatureError:
        raise errors.ApiError(401, errors.TOKEN_EXPIRED, "Refresh token has expired.") from None
    except jwt.PyJWTError:
        raise errors.ApiError(401, errors.TOKEN_INVALID, "Refresh token is invalid.") from None
    jti = payload.get("jti")
    user_id = payload.get("sub")
    if not isinstance(jti, str) or not isinstance(user_id, str):
        raise errors.ApiError(401, errors.TOKEN_INVALID, "Refresh token is invalid.")
    row = db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == hash_token(jti))
    ).scalar_one_or_none()
    if row is None or row.revoked_at is not None or row.expires_at < _utcnow():
        raise errors.ApiError(401, errors.TOKEN_INVALID, "Refresh token is invalid or revoked.")
    user = db.get(User, user_id)
    if user is None or not user.is_active or user.deleted_at is not None:
        raise errors.ApiError(401, errors.UNAUTHORIZED, "User is not active.")
    new_refresh, new_jti = create_refresh_token(user.id)
    _revoke_refresh_row(db, jti, hash_token(new_jti))
    role_name = user.role.name if user.role is not None else ""
    access = create_access_token(
        user_id=user.id,
        email=user.email,
        role=role_name,
        branch_id=_primary_branch(user),
        branches=_branches_for(user),
    )
    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=hash_token(new_jti),
            expires_at=_utcnow() + timedelta(days=settings.refresh_token_expire_days),
            created_by=user.id,
        )
    )
    db.commit()
    return access, new_refresh


def logout(db: Session, refresh_token: str) -> None:
    """Revoke the refresh token (server-side revocation list)."""
    try:
        payload = jwt.decode(
            refresh_token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
            options={"verify_exp": False},
        )
    except jwt.PyJWTError:
        return
    jti = payload.get("jti")
    if isinstance(jti, str):
        _revoke_refresh_row(db, jti, None)


def setup_mfa(db: Session, user: TokenUser) -> tuple[str, str]:
    """Generate a TOTP secret for the user (stored, MFA stays disabled until
    the user confirms a code)."""
    db_user = db.get(User, user.id)
    if db_user is None:
        raise errors.ApiError(401, errors.UNAUTHORIZED, "User not found.")
    secret = generate_totp_secret()
    db_user.mfa_secret = secret
    db.commit()
    uri = totp_provisioning_uri(secret, db_user.email)
    return secret, uri


def confirm_mfa(db: Session, user: TokenUser, code: str) -> tuple[str, str]:
    """Verify a TOTP code against the setup secret, enable MFA, issue tokens."""
    db_user = db.get(User, user.id)
    if db_user is None or db_user.mfa_secret is None:
        raise errors.ApiError(400, errors.MFA_INVALID, "MFA setup has not been started.")
    if not verify_totp(db_user.mfa_secret, code):
        raise errors.ApiError(401, errors.MFA_INVALID, "Invalid authenticator code.")
    db_user.mfa_enabled = True
    db.commit()
    write_audit(db, user, "mfa_enabled", "User", db_user.id, None, None, None, None)
    db.commit()
    return _issue_tokens(db, db_user)


def verify_mfa(db: Session, mfa_token: str, code: str, ip: str | None) -> tuple[str, str]:
    """Exchange a short-lived MFA token + TOTP code for a token pair."""
    try:
        payload = decode_token(mfa_token, "mfa")
    except jwt.ExpiredSignatureError:
        raise errors.ApiError(
            401, errors.TOKEN_EXPIRED, "MFA session expired. Log in again."
        ) from None
    except jwt.PyJWTError:
        raise errors.ApiError(401, errors.TOKEN_INVALID, "MFA token is invalid.") from None
    user_id = payload.get("sub")
    if not isinstance(user_id, str):
        raise errors.ApiError(401, errors.TOKEN_INVALID, "MFA token is invalid.")
    db_user = db.get(User, user_id)
    if db_user is None or db_user.mfa_secret is None or not db_user.mfa_enabled:
        raise errors.ApiError(401, errors.MFA_INVALID, "MFA is not enabled for this user.")
    if not verify_totp(db_user.mfa_secret, code):
        raise errors.ApiError(401, errors.MFA_INVALID, "Invalid authenticator code.")
    write_audit(db, None, "login_mfa", "User", db_user.id, None, None, ip, None)
    db.commit()
    return _issue_tokens(db, db_user)


def switch_branch(db: Session, user: TokenUser, branch_id: str) -> tuple[str, str]:
    """Issue a fresh access token scoped to another of the user's branches."""
    if user.role != "Super Admin" and branch_id not in user.branches:
        raise errors.ApiError(403, errors.FORBIDDEN, "You are not assigned to that branch.")
    access = create_access_token(
        user_id=user.id,
        email=user.email,
        role=user.role,
        branch_id=branch_id,
        branches=user.branches,
    )
    return access, branch_id


def hash_password_for_seed(password: str) -> str:
    return hash_password(password)
