"""API tests — audit log written on create/update; viewer restricted to Admin/Auditor."""

from sqlalchemy import select

from app.modules.branches.models import Branch


def test_audit_entry_written_on_branch_create(client, admin_headers) -> None:
    created = client.post(
        "/branches", json={"code": "AU-01", "name": "Audit Branch"}, headers=admin_headers
    )
    assert created.status_code == 201
    branch_id = created.json()["data"]["id"]
    logs = client.get(
        "/audit-logs", params={"entity": "Branch", "action": "create"}, headers=admin_headers
    )
    assert logs.status_code == 200
    entries = [e for e in logs.json()["data"] if e["entity_id"] == branch_id]
    assert len(entries) == 1
    assert entries[0]["action"] == "create"
    assert entries[0]["new_value"]["code"] == "AU-01"


def test_audit_entry_written_on_branch_update(client, admin_headers, db) -> None:
    branch = db.execute(select(Branch).where(Branch.code == "MB-01")).scalar_one()
    updated = client.put(
        f"/branches/{branch.id}",
        json={"name": "Morbi Main Centre (Updated)"},
        headers=admin_headers,
    )
    assert updated.status_code == 200
    logs = client.get(
        "/audit-logs",
        params={"entity": "Branch", "action": "update"},
        headers=admin_headers,
    )
    entries = [e for e in logs.json()["data"] if e["entity_id"] == branch.id]
    assert len(entries) >= 1
    assert entries[0]["old_value"]["name"] == "Morbi Main Centre"


def test_audit_log_forbidden_for_donor_staff(client, donor_staff_headers) -> None:
    response = client.get("/audit-logs", headers=donor_staff_headers)
    assert response.status_code == 403


def test_audit_log_readable_by_auditor(client, auditor_headers) -> None:
    response = client.get("/audit-logs", headers=auditor_headers)
    assert response.status_code == 200
    assert "total" in response.json()["meta"]


def test_audit_log_has_no_delete_endpoint(client, admin_headers) -> None:
    response = client.delete("/audit-logs/some-id", headers=admin_headers)
    assert response.status_code in (404, 405)
