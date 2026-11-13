"""Users / roles router."""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.deps import TokenUser, get_client_ip, get_current_user, get_db, require_permission
from app.core.envelope import (
    SuccessEnvelope,
    make_meta,
    make_page_meta,
    paginate_params,
)
from app.modules.users_roles import service
from app.modules.users_roles.schemas import (
    BranchRef,
    ChangePasswordIn,
    ResetPasswordIn,
    RoleOut,
    UserCreate,
    UserDelete,
    UserOut,
    UserUpdate,
)

router = APIRouter(tags=["users", "roles"])


def _to_out(db: Session, row: object) -> UserOut:
    from app.modules.users_roles.models import User

    assert isinstance(row, User)
    role_name = row.role.name if row.role is not None else ""
    return UserOut(
        id=row.id,
        email=row.email,
        full_name=row.full_name,
        mobile=row.mobile,
        role_id=row.role_id,
        role=role_name,
        branches=[BranchRef(**b) for b in service._branches_out(db, row)],
        is_active=row.is_active,
        mfa_enabled=row.mfa_enabled,
        last_login_at=row.last_login_at,
        created_at=row.created_at,
    )


@router.get("/users", response_model=SuccessEnvelope[list[UserOut]])
def list_users(
    request: Request,
    page: int = 1,
    page_size: int = Query(default=20, alias="pageSize"),
    user: TokenUser = Depends(require_permission("users:read")),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    page, page_size = paginate_params(page, page_size)
    rows, total = service.list_users(db, user, page, page_size)
    return {
        "success": True,
        "data": [_to_out(db, r) for r in rows],
        "meta": make_page_meta(request.state.request_id, page, page_size, total),
    }


@router.get("/users/{user_id}", response_model=SuccessEnvelope[UserOut])
def get_user(
    request: Request,
    user_id: str,
    user: TokenUser = Depends(require_permission("users:read")),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    row = service.get_user(db, user, user_id)
    return {"success": True, "data": _to_out(db, row), "meta": make_meta(request.state.request_id)}


@router.post("/users", response_model=SuccessEnvelope[UserOut], status_code=201)
def create_user(
    request: Request,
    payload: UserCreate,
    user: TokenUser = Depends(require_permission("users:create")),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    row = service.create_user(db, user, payload, get_client_ip(request))
    return {"success": True, "data": _to_out(db, row), "meta": make_meta(request.state.request_id)}


@router.put("/users/{user_id}", response_model=SuccessEnvelope[UserOut])
def update_user(
    request: Request,
    user_id: str,
    payload: UserUpdate,
    user: TokenUser = Depends(require_permission("users:update")),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    row = service.update_user(db, user, user_id, payload, get_client_ip(request))
    return {"success": True, "data": _to_out(db, row), "meta": make_meta(request.state.request_id)}


@router.delete("/users/{user_id}", response_model=SuccessEnvelope[UserOut])
def delete_user(
    request: Request,
    user_id: str,
    payload: UserDelete,
    user: TokenUser = Depends(require_permission("users:delete")),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    row = service.delete_user(db, user, user_id, payload.reason, get_client_ip(request))
    return {"success": True, "data": _to_out(db, row), "meta": make_meta(request.state.request_id)}


@router.post("/users/{user_id}/reset-password", response_model=SuccessEnvelope[UserOut])
def reset_password(
    request: Request,
    user_id: str,
    payload: ResetPasswordIn,
    user: TokenUser = Depends(require_permission("users:update")),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    row = service.reset_password(db, user, user_id, payload.new_password, get_client_ip(request))
    return {"success": True, "data": _to_out(db, row), "meta": make_meta(request.state.request_id)}


@router.post("/users/me/change-password", response_model=SuccessEnvelope[dict[str, bool]])
def change_password(
    request: Request,
    payload: ChangePasswordIn,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    service.change_own_password(db, user, payload.current_password, payload.new_password)
    return {
        "success": True,
        "data": {"changed": True},
        "meta": make_meta(request.state.request_id),
    }


@router.get("/roles", response_model=SuccessEnvelope[list[RoleOut]])
def list_roles(
    request: Request,
    user: TokenUser = Depends(require_permission("roles:read")),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    rows = service.list_roles(db)
    return {
        "success": True,
        "data": [RoleOut(**r) for r in rows],
        "meta": make_meta(request.state.request_id),
    }
