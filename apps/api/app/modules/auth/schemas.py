"""Auth schemas."""

from pydantic import BaseModel, Field


class LoginIn(BaseModel):
    email: str = Field(min_length=3, max_length=200)
    password: str = Field(min_length=1, max_length=200)


class LoginOut(BaseModel):
    access_token: str | None = None
    refresh_token: str | None = None
    token_type: str | None = None
    mfa_required: bool = False
    mfa_setup_required: bool = False
    mfa_token: str | None = None


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshIn(BaseModel):
    refresh_token: str


class LogoutIn(BaseModel):
    refresh_token: str


class MfaSetupOut(BaseModel):
    secret: str
    provisioning_uri: str


class MfaConfirmIn(BaseModel):
    code: str = Field(min_length=6, max_length=6)


class MfaVerifyIn(BaseModel):
    mfa_token: str
    code: str = Field(min_length=6, max_length=6)


class SwitchBranchIn(BaseModel):
    branch_id: str


class SwitchBranchOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    branch_id: str
