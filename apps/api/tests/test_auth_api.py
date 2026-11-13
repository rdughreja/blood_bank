"""API tests — login, lockout, MFA, refresh rotation, logout, branch switch."""

import pyotp
from sqlalchemy import select

from app.modules.branches.models import Branch


def test_login_success_donor_staff(client, donor_staff_headers) -> None:
    assert donor_staff_headers["Authorization"].startswith("Bearer ")


def test_login_wrong_password_401(client) -> None:
    response = client.post(
        "/auth/login", json={"email": "donor.staff@demo.local", "password": "WrongPass!1"}
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_login_unknown_email_401(client) -> None:
    response = client.post(
        "/auth/login", json={"email": "ghost@demo.local", "password": "Whatever!123"}
    )
    assert response.status_code == 401


def test_lockout_after_five_failed_attempts(client, db) -> None:
    email = "donor.staff@demo.local"
    for _ in range(5):
        response = client.post("/auth/login", json={"email": email, "password": "WrongPass!1"})
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "ACCOUNT_LOCKED"
    # Even the right password is refused while locked.
    response = client.post("/auth/login", json={"email": email, "password": "Demo@123456"})
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "ACCOUNT_LOCKED"


def test_mfa_required_for_admin_role(client) -> None:
    """Branch Admin login returns an MFA challenge, not tokens."""
    response = client.post(
        "/auth/login",
        json={"email": "branch.admin@demo.local", "password": "Demo@123456"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["mfa_required"] is True
    assert data["access_token"] is None
    assert data["mfa_token"] is not None


def test_mfa_verify_wrong_code_401(client) -> None:
    response = client.post(
        "/auth/login",
        json={"email": "branch.admin@demo.local", "password": "Demo@123456"},
    )
    mfa_token = response.json()["data"]["mfa_token"]
    verify = client.post("/auth/mfa/verify", json={"mfa_token": mfa_token, "code": "000000"})
    assert verify.status_code == 401
    assert verify.json()["error"]["code"] == "MFA_INVALID"


def test_mfa_setup_and_verify_flow(client) -> None:
    response = client.post(
        "/auth/login",
        json={"email": "medical.officer@demo.local", "password": "Demo@123456"},
    )
    mfa_token = response.json()["data"]["mfa_token"]
    setup = client.post("/auth/mfa/setup", headers={"Authorization": f"Bearer {mfa_token}"})
    assert setup.status_code == 200
    secret = setup.json()["data"]["secret"]
    code = pyotp.TOTP(secret).now()
    confirm = client.post(
        "/auth/mfa/confirm",
        json={"code": code},
        headers={"Authorization": f"Bearer {mfa_token}"},
    )
    assert confirm.status_code == 200
    tokens = confirm.json()["data"]
    assert tokens["access_token"]
    # The confirmed token works.
    me = client.get("/branches", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert me.status_code == 200


def test_refresh_rotation_revokes_old_token(client) -> None:
    login = client.post(
        "/auth/login", json={"email": "donor.staff@demo.local", "password": "Demo@123456"}
    )
    tokens = login.json()["data"]
    refresh1 = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert refresh1.status_code == 200
    # The old refresh token is now revoked.
    refresh2 = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert refresh2.status_code == 401
    # The new refresh token works.
    new_tokens = refresh1.json()["data"]
    refresh3 = client.post("/auth/refresh", json={"refresh_token": new_tokens["refresh_token"]})
    assert refresh3.status_code == 200


def test_logout_revokes_refresh_token(client) -> None:
    login = client.post(
        "/auth/login", json={"email": "donor.staff@demo.local", "password": "Demo@123456"}
    )
    tokens = login.json()["data"]
    logout = client.post("/auth/logout", json={"refresh_token": tokens["refresh_token"]})
    assert logout.status_code == 200
    refresh = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert refresh.status_code == 401


def test_switch_branch(client, admin_headers, db) -> None:
    branch = db.execute(select(Branch).where(Branch.code == "RJ-01")).scalar_one()
    response = client.post(
        "/auth/switch-branch", json={"branch_id": branch.id}, headers=admin_headers
    )
    assert response.status_code == 200
    assert response.json()["data"]["branch_id"] == branch.id
    # The new token works.
    me = client.get(
        "/branches",
        headers={"Authorization": f"Bearer {response.json()['data']['access_token']}"},
    )
    assert me.status_code == 200


def test_switch_branch_forbidden_for_unassigned_branch(client, donor_staff_headers, db) -> None:
    branch = db.execute(select(Branch).where(Branch.code == "AH-01")).scalar_one()
    response = client.post(
        "/auth/switch-branch", json={"branch_id": branch.id}, headers=donor_staff_headers
    )
    assert response.status_code == 403


def test_unauthenticated_request_401(client) -> None:
    response = client.get("/branches")
    assert response.status_code == 401
    response = client.get("/branches", headers={"Authorization": "Bearer nonsense"})
    assert response.status_code == 401
