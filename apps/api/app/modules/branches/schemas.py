"""Branch schemas."""

from pydantic import BaseModel, Field

from app.core.envelope import UtcDateTime


class BranchCreate(BaseModel):
    code: str = Field(min_length=1, max_length=20)
    name: str = Field(min_length=1, max_length=200)
    address: str | None = Field(default=None, max_length=500)
    licence_no: str | None = Field(default=None, max_length=100)
    is_storage_centre: bool = False


class BranchUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    address: str | None = Field(default=None, max_length=500)
    licence_no: str | None = Field(default=None, max_length=100)
    is_storage_centre: bool | None = None
    is_active: bool | None = None


class BranchDelete(BaseModel):
    reason: str = Field(min_length=1, max_length=500)


class BranchOut(BaseModel):
    id: str
    code: str
    name: str
    address: str | None
    licence_no: str | None
    is_storage_centre: bool
    is_active: bool
    created_at: UtcDateTime
    updated_at: UtcDateTime
