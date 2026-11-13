"""Branch router — CRUD for /branches."""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.deps import TokenUser, get_client_ip, get_db, require_permission
from app.core.envelope import (
    SuccessEnvelope,
    make_meta,
    make_page_meta,
    paginate_params,
)
from app.modules.branches import service
from app.modules.branches.schemas import (
    BranchCreate,
    BranchDelete,
    BranchOut,
    BranchUpdate,
)

router = APIRouter(prefix="/branches", tags=["branches"])


def _to_out(row: object) -> BranchOut:
    from app.modules.branches.models import Branch

    assert isinstance(row, Branch)
    return BranchOut(
        id=row.id,
        code=row.code,
        name=row.name,
        address=row.address,
        licence_no=row.licence_no,
        is_storage_centre=row.is_storage_centre,
        is_active=row.is_active,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


@router.get("", response_model=SuccessEnvelope[list[BranchOut]])
def list_branches(
    request: Request,
    page: int = 1,
    page_size: int = Query(default=20, alias="pageSize"),
    user: TokenUser = Depends(require_permission("branches:read")),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    page, page_size = paginate_params(page, page_size)
    rows, total = service.list_branches(db, user, page, page_size)
    return {
        "success": True,
        "data": [_to_out(r) for r in rows],
        "meta": make_page_meta(request.state.request_id, page, page_size, total),
    }


@router.get("/{branch_id}", response_model=SuccessEnvelope[BranchOut])
def get_branch(
    request: Request,
    branch_id: str,
    user: TokenUser = Depends(require_permission("branches:read")),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    row = service.get_branch(db, user, branch_id)
    return {"success": True, "data": _to_out(row), "meta": make_meta(request.state.request_id)}


@router.post("", response_model=SuccessEnvelope[BranchOut], status_code=201)
def create_branch(
    request: Request,
    payload: BranchCreate,
    user: TokenUser = Depends(require_permission("branches:create")),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    row = service.create_branch(db, user, payload, get_client_ip(request))
    return {"success": True, "data": _to_out(row), "meta": make_meta(request.state.request_id)}


@router.put("/{branch_id}", response_model=SuccessEnvelope[BranchOut])
def update_branch(
    request: Request,
    branch_id: str,
    payload: BranchUpdate,
    user: TokenUser = Depends(require_permission("branches:update")),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    row = service.update_branch(db, user, branch_id, payload, get_client_ip(request))
    return {"success": True, "data": _to_out(row), "meta": make_meta(request.state.request_id)}


@router.delete("/{branch_id}", response_model=SuccessEnvelope[BranchOut])
def delete_branch(
    request: Request,
    branch_id: str,
    payload: BranchDelete,
    user: TokenUser = Depends(require_permission("branches:delete")),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    # "branches:delete" is held only by Super Admin ("*" covers it).
    row = service.delete_branch(db, user, branch_id, payload.reason, get_client_ip(request))
    return {"success": True, "data": _to_out(row), "meta": make_meta(request.state.request_id)}
