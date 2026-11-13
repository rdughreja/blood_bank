"""Settings schemas."""

from typing import Any

from pydantic import BaseModel, Field


class SettingOut(BaseModel):
    id: str
    key: str
    value: Any
    scope: str
    branch_id: str | None
    confirm_with_mo: bool
    label: str | None
    description: str | None


class SettingUpsert(BaseModel):
    key: str = Field(min_length=1, max_length=100)
    value: Any
    scope: str = Field(default="global", pattern="^(global|branch)$")
    branch_id: str | None = None
    confirm_with_mo: bool = False
    label: str | None = None
    description: str | None = None
