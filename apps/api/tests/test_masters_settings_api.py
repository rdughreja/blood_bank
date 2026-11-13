"""API tests — masters CRUD and settings API."""

from sqlalchemy import select

from app.modules.branches.models import Branch


def test_masters_list_seeded_blood_groups(client, admin_headers) -> None:
    response = client.get("/masters/blood_group", headers=admin_headers)
    assert response.status_code == 200
    codes = [m["code"] for m in response.json()["data"]]
    assert codes == ["A+", "A-", "AB+", "AB-", "B+", "B-", "O+", "O-"]
    assert response.json()["meta"]["total"] == 8


def test_masters_unknown_type_404(client, admin_headers) -> None:
    response = client.get("/masters/nope", headers=admin_headers)
    assert response.status_code == 404


def test_masters_create_update_soft_delete(client, admin_headers) -> None:
    created = client.post(
        "/masters/test_name",
        json={"code": "HBV-DNA", "name": "HBV DNA NAT"},
        headers=admin_headers,
    )
    assert created.status_code == 201, created.text
    master_id = created.json()["data"]["id"]
    updated = client.put(
        f"/masters/{master_id}", json={"name": "HBV DNA (NAT)"}, headers=admin_headers
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["name"] == "HBV DNA (NAT)"
    deleted = client.request(
        "DELETE", f"/masters/{master_id}", json={"reason": "duplicate"}, headers=admin_headers
    )
    assert deleted.status_code == 200
    listed = client.get("/masters/test_name", headers=admin_headers)
    codes = [m["code"] for m in listed.json()["data"]]
    assert "HBV-DNA" not in codes  # soft-deleted rows are hidden


def test_masters_duplicate_code_409(client, admin_headers) -> None:
    response = client.post(
        "/masters/blood_group", json={"code": "A+", "name": "Duplicate"}, headers=admin_headers
    )
    assert response.status_code == 409


def test_settings_list_has_clinical_defaults(client, admin_headers) -> None:
    response = client.get("/settings", headers=admin_headers)
    assert response.status_code == 200
    by_key = {s["key"]: s for s in response.json()["data"]}
    assert by_key["eligibility.min_hb_g_dl"]["value"] == 12.5
    assert by_key["eligibility.min_hb_g_dl"]["confirm_with_mo"] is True
    assert by_key["shelf_life.wb_prbc_days"]["value"] == 35
    assert by_key["crossmatch.hold_hours"]["value"] == 72


def test_settings_branch_override(client, admin_headers, db) -> None:
    branch = db.execute(select(Branch).where(Branch.code == "MB-01")).scalar_one()
    updated = client.put(
        "/settings",
        json={
            "key": "alerts.expiry_warning_days",
            "value": 10,
            "scope": "branch",
            "branch_id": branch.id,
        },
        headers=admin_headers,
    )
    assert updated.status_code == 200
    listed = client.get("/settings", params={"branch_id": branch.id}, headers=admin_headers)
    by_key = {s["key"]: s for s in listed.json()["data"]}
    assert by_key["alerts.expiry_warning_days"]["value"] == 10
    # Another branch still sees the global default (7).
    other = db.execute(select(Branch).where(Branch.code == "RJ-01")).scalar_one()
    listed2 = client.get("/settings", params={"branch_id": other.id}, headers=admin_headers)
    by_key2 = {s["key"]: s for s in listed2.json()["data"]}
    assert by_key2["alerts.expiry_warning_days"]["value"] == 7


def test_settings_global_update_forbidden_for_branch_admin(client, branch_admin_headers) -> None:
    response = client.put(
        "/settings",
        json={"key": "alerts.expiry_warning_days", "value": 3, "scope": "global"},
        headers=branch_admin_headers,
    )
    assert response.status_code == 403


def test_list_pagination_envelope(client, admin_headers) -> None:
    response = client.get("/branches?page=1&pageSize=2", headers=admin_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["meta"]["page"] == 1
    assert body["meta"]["pageSize"] == 2
    assert body["meta"]["total"] == 3
    assert body["meta"]["totalPages"] == 2
    assert len(body["data"]) == 2
