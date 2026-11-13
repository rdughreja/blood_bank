"""Unit tests — password hashing, token expiry, barcode uniqueness, settings fallback."""

import re

import jwt
import pytest
from sqlalchemy import select

from app.core import errors
from app.core.security import (
    create_access_token,
    hash_password,
    validate_password_policy,
    verify_password,
)
from app.modules.barcodes.service import next_barcode
from app.modules.branches.models import Branch
from app.modules.settings.models import Setting
from app.modules.settings.service import get_effective_value, get_value


def test_password_hash_round_trip() -> None:
    hashed = hash_password("CorrectHorse!123")
    assert verify_password("CorrectHorse!123", hashed) is True
    assert verify_password("wrong-password", hashed) is False
    assert hashed != "CorrectHorse!123"


def test_password_policy() -> None:
    assert validate_password_policy("Short1!") != []
    assert validate_password_policy("alllowercase123!") != []
    assert validate_password_policy("ALLUPPERCASE123!") != []
    assert validate_password_policy("NoDigitsHere!!") != []
    assert validate_password_policy("NoSpecial12345") != []
    assert validate_password_policy("ValidPass!123") == []


def test_access_token_expiry() -> None:
    expired = create_access_token(
        user_id="u1",
        email="a@b.c",
        role="Viewer / Auditor",
        branch_id=None,
        branches=[],
        expires_minutes=-1,
    )
    with pytest.raises(jwt.ExpiredSignatureError):
        from app.core.security import decode_token

        decode_token(expired, "access")


def test_access_token_wrong_type_rejected() -> None:
    token = create_access_token(
        user_id="u1", email="a@b.c", role="Viewer / Auditor", branch_id=None, branches=[]
    )
    with pytest.raises(jwt.InvalidTokenError):
        from app.core.security import decode_token

        decode_token(token, "refresh")


def test_barcode_uniqueness_across_branches(db) -> None:
    codes: set[str] = set()
    for _ in range(200):
        row = next_barcode(db, "unit", None, None, None)
        assert re.fullmatch(r"BB-\d{8}-[A-Z2-9]{6}", row.code), row.code
        codes.add(row.code)
    assert len(codes) == 200


def test_settings_fallback_branch_to_global(db) -> None:
    branch = db.execute(select(Branch).where(Branch.code == "MB-01")).scalar_one()
    # Global default exists from seed.
    assert get_value(db, "eligibility.min_age", branch.id, None) == 18
    # Branch override wins over global.
    db.add(
        Setting(
            key="eligibility.min_age",
            value=21,
            scope="branch",
            branch_id=branch.id,
            confirm_with_mo=True,
        )
    )
    db.commit()
    assert get_effective_value(db, "eligibility.min_age", branch.id) == 21
    # Other branch still sees the global value.
    other = db.execute(select(Branch).where(Branch.code == "RJ-01")).scalar_one()
    assert get_effective_value(db, "eligibility.min_age", other.id) == 18
    # Unknown key returns None.
    assert get_effective_value(db, "does.not.exist", branch.id) is None


def test_error_envelope_shape(client) -> None:
    response = client.post("/auth/login", json={"email": "nobody@demo.local", "password": "x"})
    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == errors.INVALID_CREDENTIALS
    assert "requestId" in body["error"]
    assert body["error"]["timestamp"].endswith("Z")
