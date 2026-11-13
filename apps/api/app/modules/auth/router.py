"""Auth router — login / refresh / logout / MFA / branch switch."""

import jwt
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core import errors
from app.core.deps import TokenUser, get_client_ip, get_current_user, get_db
from app.core.envelope import SuccessEnvelope, make_meta
from app.core.rate_limit import AUTH_LIMIT, LOGIN_LIMIT, limiter
from app.core.security import decode_token
from app.modules.auth import service
from app.modules.auth.schemas import (
    LoginIn,
    LoginOut,
    LogoutIn,
    MfaConfirmIn,
    MfaSetupOut,
    MfaVerifyIn,
    RefreshIn,
    SwitchBranchIn,
    SwitchBranchOut,
    TokenPair,
)
from app.modules.users_roles.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


def get_mfa_user(request: Request, db: Session = Depends(get_db)) -> TokenUser:
    """Decode the short-lived MFA token from the Authorization header."""
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        raise errors.ApiError(401, errors.UNAUTHORIZED, "Missing MFA token.")
    token = header[len("Bearer ") :].strip()
    try:
        payload = decode_token(token, "mfa")
    except jwt.ExpiredSignatureError:
        raise errors.ApiError(401, errors.TOKEN_EXPIRED, "MFA session expired.") from None
    except jwt.PyJWTError:
        raise errors.ApiError(401, errors.TOKEN_INVALID, "MFA token is invalid.") from None
    user_id = payload.get("sub")
    if not isinstance(user_id, str):
        raise errors.ApiError(401, errors.TOKEN_INVALID, "MFA token is invalid.")
    db_user = db.get(User, user_id)
    if db_user is None:
        raise errors.ApiError(401, errors.UNAUTHORIZED, "User not found.")
    role_name = db_user.role.name if db_user.role is not None else ""
    return TokenUser(
        id=db_user.id,
        email=db_user.email,
        role=role_name,
        branch_id=None,
        branches=[ub.branch_id for ub in db_user.branches],
        db_user=db_user,
    )


@router.post("/login", response_model=SuccessEnvelope[LoginOut])
@limiter.limit(LOGIN_LIMIT)
def login(request: Request, payload: LoginIn, db: Session = Depends(get_db)) -> dict[str, object]:
    result = service.login(db, payload.email, payload.password, get_client_ip(request))
    return {"success": True, "data": result, "meta": make_meta(request.state.request_id)}


@router.post("/refresh", response_model=SuccessEnvelope[TokenPair])
@limiter.limit(AUTH_LIMIT)
def refresh(
    request: Request, payload: RefreshIn, db: Session = Depends(get_db)
) -> dict[str, object]:
    access, refresh_token = service.refresh_tokens(db, payload.refresh_token)
    return {
        "success": True,
        "data": {"access_token": access, "refresh_token": refresh_token, "token_type": "bearer"},
        "meta": make_meta(request.state.request_id),
    }


@router.post("/logout", response_model=SuccessEnvelope[dict[str, bool]])
@limiter.limit(AUTH_LIMIT)
def logout(request: Request, payload: LogoutIn, db: Session = Depends(get_db)) -> dict[str, object]:
    service.logout(db, payload.refresh_token)
    return {
        "success": True,
        "data": {"loggedOut": True},
        "meta": make_meta(request.state.request_id),
    }


@router.post("/mfa/setup", response_model=SuccessEnvelope[MfaSetupOut])
def mfa_setup(
    request: Request,
    user: TokenUser = Depends(get_mfa_user),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    secret, uri = service.setup_mfa(db, user)
    return {
        "success": True,
        "data": {"secret": secret, "provisioning_uri": uri},
        "meta": make_meta(request.state.request_id),
    }


@router.post("/mfa/confirm", response_model=SuccessEnvelope[TokenPair])
def mfa_confirm(
    request: Request,
    payload: MfaConfirmIn,
    user: TokenUser = Depends(get_mfa_user),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    access, refresh_token = service.confirm_mfa(db, user, payload.code)
    return {
        "success": True,
        "data": {"access_token": access, "refresh_token": refresh_token, "token_type": "bearer"},
        "meta": make_meta(request.state.request_id),
    }


@router.post("/mfa/verify", response_model=SuccessEnvelope[TokenPair])
@limiter.limit(AUTH_LIMIT)
def mfa_verify(
    request: Request, payload: MfaVerifyIn, db: Session = Depends(get_db)
) -> dict[str, object]:
    access, refresh_token = service.verify_mfa(
        db, payload.mfa_token, payload.code, get_client_ip(request)
    )
    return {
        "success": True,
        "data": {"access_token": access, "refresh_token": refresh_token, "token_type": "bearer"},
        "meta": make_meta(request.state.request_id),
    }


@router.post("/switch-branch", response_model=SuccessEnvelope[SwitchBranchOut])
def switch_branch(
    request: Request,
    payload: SwitchBranchIn,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    access, branch_id = service.switch_branch(db, user, payload.branch_id)
    return {
        "success": True,
        "data": {"access_token": access, "token_type": "bearer", "branch_id": branch_id},
        "meta": make_meta(request.state.request_id),
    }
