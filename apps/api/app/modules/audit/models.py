"""Audit log model (Phase 1) — append-only; no edit/delete API exists."""

from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"

    user_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    user_email: Mapped[str | None] = mapped_column(String(200), nullable=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # create/update/delete/login
    entity: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    old_value: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    new_value: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(50), nullable=True)
    branch_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
