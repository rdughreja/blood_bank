"""Barcode service — server-generated unique IDs, never reused.

Format: BB-YYYYMMDD-XXXXXX (see docs/decisions.md). Every issued code is
recorded in the `barcodes` table with a unique constraint; generation retries
on collision.
"""

from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.audit import write_audit
from app.core.deps import TokenUser
from app.core.security import random_code
from app.modules.barcodes.models import Barcode


def next_barcode(
    db: Session,
    barcode_type: str,
    branch_id: str | None,
    user: TokenUser | None,
    ip: str | None,
    entity_type: str | None = None,
    entity_id: str | None = None,
) -> Barcode:
    today = datetime.now(UTC).strftime("%Y%m%d")
    last_error: Exception | None = None
    for _ in range(10):
        code = f"BB-{today}-{random_code(6)}"
        row = Barcode(
            code=code,
            barcode_type=barcode_type,
            branch_id=branch_id,
            entity_type=entity_type,
            entity_id=entity_id,
            created_by=user.id if user else None,
        )
        db.add(row)
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            last_error = exc
            continue
        db.refresh(row)
        if user is not None:
            write_audit(db, user, "create", "Barcode", row.id, None, {"code": code}, ip, branch_id)
            db.commit()
        return row
    raise RuntimeError(f"Could not generate a unique barcode after 10 attempts: {last_error}")
