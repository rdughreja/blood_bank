"""Settings model (Phase 1) — key-value, per branch with global fallback."""

from sqlalchemy import JSON, Boolean, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class Setting(Base, TimestampMixin):
    __tablename__ = "settings"
    __table_args__ = (
        UniqueConstraint("key", "scope", "branch_id", name="uq_setting_key_scope_branch"),
    )

    key: Mapped[str] = mapped_column(String(100), nullable=False)
    # JSON value — numbers, strings, booleans or objects.
    value: Mapped[object] = mapped_column(JSON, nullable=False)
    # "global" or "branch". Branch values override global ones.
    scope: Mapped[str] = mapped_column(String(20), nullable=False, default="global")
    branch_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    # True for clinical defaults — UI must label "confirm with Medical Officer".
    confirm_with_mo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    label: Mapped[str | None] = mapped_column(String(200), nullable=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
