"""Master data schemas."""

from typing import Any

from pydantic import BaseModel, Field

from app.core.envelope import UtcDateTime


class MasterCreate(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=200)
    extra: dict[str, Any] | None = None
    branch_id: str | None = None


class MasterUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    extra: dict[str, Any] | None = None
    is_active: bool | None = None


class MasterDelete(BaseModel):
    reason: str = Field(min_length=1, max_length=500)


class MasterOut(BaseModel):
    id: str
    type: str
    code: str
    name: str
    extra: dict[str, Any] | None
    is_active: bool
    branch_id: str | None
    created_at: UtcDateTime
