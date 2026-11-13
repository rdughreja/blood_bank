"""API tests — branch isolation (the most important tests in Phase 1).

A user of Branch A must get no Branch B records, and a direct ID lookup of a
Branch B record must return 404 (never reveal that it exists).
"""

from sqlalchemy import select

from app.modules.branches.models import Branch
from app.modules.users_roles.models import Role, User, UserBranch


def _make_branch_user(
    db, client, branch_code: str, email: str, role_name: str = "Donor Staff / Counsellor"
) -> dict[str, str]:
    """Create a user assigned to one branch only; return headers."""
    branch = db.execute(select(Branch).where(Branch.code == branch_code)).scalar_one()
    role = db.execute(select(Role).where(Role.name == role_name)).scalar_one()
    from app.core.crypto import blind_index
    from app.core.security import hash_password

    user = User(
        email=email,
        email_lookup=blind_index(email),
        full_name=f"Staff {branch_code}",
        password_hash=hash_password("StaffPass!123"),
        role_id=role.id,
    )
    db.add(user)
    db.flush()
    db.add(UserBranch(user_id=user.id, branch_id=branch.id, is_primary=True))
    db.commit()
    from tests.conftest import login

    return login(client, email, "StaffPass!123")


def test_branch_user_sees_only_own_branch(client, db) -> None:
    headers = _make_branch_user(db, client, "MB-01", "staff.mb01@demo.local")
    response = client.get("/branches", headers=headers)
    assert response.status_code == 200
    codes = [b["code"] for b in response.json()["data"]]
    assert codes == ["MB-01"]


def test_branch_user_cannot_fetch_other_branch_by_id(client, db) -> None:
    headers = _make_branch_user(db, client, "MB-01", "staff.mb02@demo.local")
    other = db.execute(select(Branch).where(Branch.code == "RJ-01")).scalar_one()
    response = client.get(f"/branches/{other.id}", headers=headers)
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_branch_user_cannot_see_other_branch_users(client, db) -> None:
    # Branch Admins (they hold users:read) scoped to one branch each.
    _make_branch_user(db, client, "MB-01", "staff.a@demo.local", "Branch Admin")
    headers_b = _make_branch_user(db, client, "RJ-01", "staff.b@demo.local", "Branch Admin")
    # User B lists users — must not see user A (different branch).
    response = client.get("/users", headers=headers_b)
    assert response.status_code == 200
    emails = [u["email"] for u in response.json()["data"]]
    assert "staff.a@demo.local" not in emails
    assert "staff.b@demo.local" in emails


def test_branch_admin_cannot_create_user_in_other_branch(client, db, branch_admin_headers) -> None:
    # Branch Admin (MB-01) tries to create a user assigned to AH-01.
    ah = db.execute(select(Branch).where(Branch.code == "AH-01")).scalar_one()
    role = db.execute(select(Role).where(Role.name == "Donor Staff / Counsellor")).scalar_one()
    response = client.post(
        "/users",
        json={
            "email": "outsider@demo.local",
            "full_name": "Outsider",
            "password": "Outsider!123",
            "role_id": role.id,
            "branch_ids": [ah.id],
        },
        headers=branch_admin_headers,
    )
    assert response.status_code == 403


def test_branch_user_cannot_read_other_branch_master(client, db) -> None:
    # Create a branch-scoped master for RJ-01 as admin, then check MB-01 user.

    headers = _make_branch_user(db, client, "MB-01", "staff.m@demo.local")
    # Use the admin client to create the RJ-01 master.
    from tests.conftest import login

    admin = login(client, "admin@bloodbank.local", "Admin@123456")
    rj = db.execute(select(Branch).where(Branch.code == "RJ-01")).scalar_one()
    created = client.post(
        "/masters/ward",
        json={"code": "RJ-WARD-1", "name": "RJ Ward 1", "branch_id": rj.id},
        headers=admin,
    )
    assert created.status_code == 201, created.text
    # MB-01 user lists wards — must not see the RJ-01 master.
    listed = client.get("/masters/ward", headers=headers)
    assert listed.status_code == 200
    codes = [m["code"] for m in listed.json()["data"]]
    assert "RJ-WARD-1" not in codes
