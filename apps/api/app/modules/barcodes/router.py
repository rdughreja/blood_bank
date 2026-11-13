"""Barcode router — GET /barcodes/next (internal service, not a free-for-all)."""

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.deps import TokenUser, get_client_ip, get_db, require_permission
from app.core.envelope import SuccessEnvelope, make_meta
from app.modules.barcodes import service

router = APIRouter(prefix="/barcodes", tags=["barcodes"])


class BarcodeOut(BaseModel):
    id: str
    code: str
    barcode_type: str
    branch_id: str | None


@router.get("/next", response_model=SuccessEnvelope[BarcodeOut])
def next_barcode(
    request: Request,
    type: str = "unit",
    branch_id: str | None = None,
    user: TokenUser = Depends(require_permission("barcodes:read")),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    row = service.next_barcode(db, type, branch_id, user, get_client_ip(request))
    return {
        "success": True,
        "data": BarcodeOut(
            id=row.id, code=row.code, barcode_type=row.barcode_type, branch_id=row.branch_id
        ),
        "meta": make_meta(request.state.request_id),
    }
