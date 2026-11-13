"""Barcode model (Phase 1) — every issued barcode is recorded once, never reused."""

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class Barcode(Base, TimestampMixin):
    __tablename__ = "barcodes"
    __table_args__ = (UniqueConstraint("code", name="uq_barcode_code"),)

    # Format: BB-YYYYMMDD-XXXXXX (see docs/decisions.md).
    code: Mapped[str] = mapped_column(String(30), nullable=False)
    barcode_type: Mapped[str] = mapped_column(String(50), nullable=False)
    branch_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    entity_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    entity_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
