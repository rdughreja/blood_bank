"""Master data model (Phase 1) — one table for all master types."""

from sqlalchemy import JSON, Boolean, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin

# Master types — the plan's Phase 1 masters list.
MASTER_BLOOD_GROUP = "blood_group"
MASTER_COMPONENT_TYPE = "component_type"
MASTER_TEST_NAME = "test_name"
MASTER_DEFERRAL_REASON = "deferral_reason"
MASTER_DISCARD_REASON = "discard_reason"
MASTER_HOSPITAL = "hospital"
MASTER_WARD = "ward"
MASTER_CHARGE = "charge"

MASTER_TYPES: list[str] = [
    MASTER_BLOOD_GROUP,
    MASTER_COMPONENT_TYPE,
    MASTER_TEST_NAME,
    MASTER_DEFERRAL_REASON,
    MASTER_DISCARD_REASON,
    MASTER_HOSPITAL,
    MASTER_WARD,
    MASTER_CHARGE,
]


class MasterData(Base, TimestampMixin):
    __tablename__ = "master_data"
    __table_args__ = (
        UniqueConstraint("type", "code", "branch_id", name="uq_master_type_code_branch"),
    )

    type: Mapped[str] = mapped_column(String(50), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    # Extra JSON — e.g. charge amount in paise: {"amount_paise": 150000}.
    extra: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # Null branch_id = global master, visible to all branches.
    branch_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
