"""API tests — RBAC: 403 for every role/action pair the RBAC table forbids."""

import pytest
from sqlalchemy import select

from app.modules.branches.models import Branch
from app.modules.users_roles.models import Role


def _role_id(db, name: str) -> str:
    return db.execute(select(Role).where(Role.name == name)).scalar_one().id


def _branch_id(db, code: str) -> str:
    return db.execute(select(Branch).where(Branch.code == code)).scalar_one().id


# (fixture-name, method, path, body, expect) — all must be 403.
FORBIDDEN: list[tuple[str, str, str, dict[str, object] | None]] = [
    ("donor_staff_headers", "POST", "/branches", {"code": "XX-01", "name": "Nope"}),
    ("donor_staff_headers", "POST", "/users", {}),
    ("donor_staff_headers", "POST", "/masters/blood_group", {"code": "X", "name": "X"}),
    ("donor_staff_headers", "PUT", "/settings", {"key": "x", "value": 1}),
    ("donor_staff_headers", "GET", "/audit-logs", None),
    ("donor_staff_headers", "GET", "/roles", None),
    ("auditor_headers", "POST", "/branches", {"code": "XX-01", "name": "Nope"}),
    ("auditor_headers", "POST", "/users", {}),
    ("auditor_headers", "PUT", "/settings", {"key": "x", "value": 1}),
    ("auditor_headers", "DELETE", "/users/does-not-matter", {"reason": "x"}),
    ("medical_officer_headers", "POST", "/branches", {"code": "XX-01", "name": "Nope"}),
    ("medical_officer_headers", "POST", "/users", {}),
    ("medical_officer_headers", "POST", "/masters/blood_group", {"code": "X", "name": "X"}),
    ("medical_officer_headers", "PUT", "/settings", {"key": "x", "value": 1}),
    ("branch_admin_headers", "PUT", "/settings", {"key": "x", "value": 1, "scope": "global"}),
    ("branch_admin_headers", "POST", "/masters/blood_group", {"code": "X", "name": "X"}),
]


@pytest.mark.parametrize("headers_fixture,method,path,body", FORBIDDEN)
def test_forbidden_role_action_pairs(client, request, headers_fixture, method, path, body) -> None:
    headers = request.getfixturevalue(headers_fixture)
    response = client.request(method, path, json=body, headers=headers)
    assert response.status_code == 403, (method, path, response.text)
    assert response.json()["error"]["code"] == "FORBIDDEN"


def test_branch_admin_cannot_create_global_master(client, branch_admin_headers) -> None:
    # branch_id null = global master -> Branch Admin is forbidden.
    response = client.post(
        "/masters/blood_group",
        json={"code": "ZZ", "name": "Zed", "branch_id": None},
        headers=branch_admin_headers,
    )
    assert response.status_code == 403


def test_super_admin_can_do_everything(client, admin_headers, db) -> None:
    response = client.post(
        "/branches",
        json={"code": "ZZ-01", "name": "Zed Branch"},
        headers=admin_headers,
    )
    assert response.status_code == 201, response.text
    response = client.put(
        "/settings",
        json={"key": "test.super_admin", "value": True, "scope": "global"},
        headers=admin_headers,
    )
    assert response.status_code == 200, response.text
    response = client.get("/audit-logs", headers=admin_headers)
    assert response.status_code == 200


def test_auditor_can_read_but_not_write(client, auditor_headers) -> None:
    assert client.get("/branches", headers=auditor_headers).status_code == 200
    assert client.get("/audit-logs", headers=auditor_headers).status_code == 200
    assert client.get("/masters/blood_group", headers=auditor_headers).status_code == 200
    assert client.get("/settings", headers=auditor_headers).status_code == 200
    response = client.post(
        "/branches", json={"code": "ZZ-02", "name": "Nope"}, headers=auditor_headers
    )
    assert response.status_code == 403
