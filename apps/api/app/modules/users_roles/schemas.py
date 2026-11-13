"""User / role schemas."""

from pydantic import BaseModel, Field

from app.core.envelope import UtcDateTime


class BranchRef(BaseModel):
    id: str
    code: str
    name: str


class UserCreate(BaseModel):
    email: str = Field(min_length=3, max_length=200)
    full_name: str = Field(min_length=1, max_length=200)
    mobile: str | None = Field(default=None, max_length=20)
    password: str = Field(min_length=1, max_length=200)
    role_id: str
    branch_ids: list[str] = Field(default_factory=list)
    primary_branch_id: str | None = None


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, max_length=200)
    mobile: str | None = Field(default=None, max_length=20)
    role_id: str | None = None
    branch_ids: list[str] | None = None
    primary_branch_id: str | None = None
    is_active: bool | None = None


class UserDelete(BaseModel):
    reason: str = Field(min_length=1, max_length=500)


class ResetPasswordIn(BaseModel):
    new_password: str = Field(min_length=1, max_length=200)


class ChangePasswordIn(BaseModel):
    current_password: str = Field(min_length=1, max_length=200)
    new_password: str = Field(min_length=1, max_length=200)


class UserOut(BaseModel):
    id: str
    email: str
    full_name: str
    mobile: str | None
    role_id: str
    role: str
    branches: list[BranchRef]
    is_active: bool
    mfa_enabled: bool
    last_login_at: UtcDateTime | None
    created_at: UtcDateTime


class RoleOut(BaseModel):
    id: str
    name: str
    description: str | None
    permissions: list[str]
