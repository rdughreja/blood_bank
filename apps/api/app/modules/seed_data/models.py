"""Seed-only tables (Phase 1).

The Phase 1 seed script requires 200 fake donors and sample camps as demo
data, but NO donor/camp features are built in Phase 1. These minimal tables
exist ONLY to hold seed rows. There are no routers, services, screens or API
endpoints for them in this phase; they are built properly in Phase 2.
"""

from sqlalchemy import Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.crypto import EncryptedString
from app.db.base import Base, TimestampMixin


class SeedDonor(Base, TimestampMixin):
    __tablename__ = "donors"

    donor_code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    date_of_birth: Mapped[object] = mapped_column(Date, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    blood_group: Mapped[str | None] = mapped_column(String(10), nullable=True)
    mobile: Mapped[str | None] = mapped_column(EncryptedString(500), nullable=True)
    email: Mapped[str | None] = mapped_column(EncryptedString(500), nullable=True)
    branch_id: Mapped[str | None] = mapped_column(String(36), nullable=True)


class SeedCamp(Base, TimestampMixin):
    __tablename__ = "camps"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    organizer: Mapped[str | None] = mapped_column(String(200), nullable=True)
    venue: Mapped[str | None] = mapped_column(String(300), nullable=True)
    camp_date: Mapped[object] = mapped_column(Date, nullable=True)
    target_units: Mapped[int | None] = mapped_column(Integer, nullable=True)
    branch_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="planned")
