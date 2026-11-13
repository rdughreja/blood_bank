"""Masters router — CRUD for /masters/:type."""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.deps import TokenUser, get_client_ip, get_db, require_permission
from app.core.envelope import (
    SuccessEnvelope,
    make_meta,
    make_page_meta,
    paginate_params,
)
from app.modules.masters import service
from app.modules.masters.models import MASTER_TYPES
from app.modules.masters.schemas import MasterCreate, MasterDelete, MasterOut, MasterUpdate

router = APIRouter(prefix="/masters", tags=["masters"])


def _to_out(row: object) -> MasterOut:
    from app.modules.masters.models import MasterData

    assert isinstance(row, MasterData)
    return MasterOut(
        id=row.id,
        type=row.type,
        code=row.code,
        name=row.name,
        extra=row.extra,
        is_active=row.is_active,
        branch_id=row.branch_id,
        created_at=row.created_at,
    )


@router.get("/types", response_model=SuccessEnvelope[list[str]])
def list_master_types(
    request: Request,
    user: TokenUser = Depends(require_permission("masters:read")),
) -> dict[str, object]:
    return {
        "success": True,
        "data": MASTER_TYPES,
        "meta": make_meta(request.state.request_id),
    }


@router.get("/{master_type}", response_model=SuccessEnvelope[list[MasterOut]])
def list_masters(
    request: Request,
    master_type: str,
    page: int = 1,
    page_size: int = Query(default=20, alias="pageSize"),
    user: TokenUser = Depends(require_permission("masters:read")),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    page, page_size = paginate_params(page, page_size)
    rows, total = service.list_masters(db, user, master_type, page, page_size)
    return {
        "success": True,
        "data": [_to_out(r) for r in rows],
        "meta": make_page_meta(request.state.request_id, page, page_size, total),
    }


@router.post("/{master_type}", response_model=SuccessEnvelope[MasterOut], status_code=201)
def create_master(
    request: Request,
    master_type: str,
    payload: MasterCreate,
    user: TokenUser = Depends(require_permission("masters:create")),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    row = service.create_master(db, user, master_type, payload, get_client_ip(request))
    return {"success": True, "data": _to_out(row), "meta": make_meta(request.state.request_id)}


@router.put("/{master_id}", response_model=SuccessEnvelope[MasterOut])
def update_master(
    request: Request,
    master_id: str,
    payload: MasterUpdate,
    user: TokenUser = Depends(require_permission("masters:update")),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    row = service.update_master(db, user, master_id, payload, get_client_ip(request))
    return {"success": True, "data": _to_out(row), "meta": make_meta(request.state.request_id)}


@router.delete("/{master_id}", response_model=SuccessEnvelope[MasterOut])
def delete_master(
    request: Request,
    master_id: str,
    payload: MasterDelete,
    user: TokenUser = Depends(require_permission("masters:delete")),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    row = service.delete_master(db, user, master_id, payload.reason, get_client_ip(request))
    return {"success": True, "data": _to_out(row), "meta": make_meta(request.state.request_id)}
