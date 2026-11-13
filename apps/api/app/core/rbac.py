"""RBAC — roles and permissions from the BUILD_PLAN.md RBAC table.

Permissions are `resource:action` strings. Deny by default: if a role is not
listed for an action, the API returns 403. Server-side checks run on every
route; frontend menu hiding is not security.
"""

# Role names — exactly the RBAC table in BUILD_PLAN.md.
ROLE_SUPER_ADMIN = "Super Admin"
ROLE_BRANCH_ADMIN = "Branch Admin"
ROLE_MEDICAL_OFFICER = "Medical Officer"
ROLE_DONOR_STAFF = "Donor Staff / Counsellor"
ROLE_PHLEBOTOMIST = "Phlebotomist / Collection Staff"
ROLE_LAB_TECHNICIAN = "Lab Technician"
ROLE_LAB_INCHARGE = "Lab In-charge"
ROLE_ISSUE_STORE = "Issue / Store Staff"
ROLE_BILLING_STAFF = "Billing Staff"
ROLE_VIEWER_AUDITOR = "Viewer / Auditor"

ALL_ROLES: list[str] = [
    ROLE_SUPER_ADMIN,
    ROLE_BRANCH_ADMIN,
    ROLE_MEDICAL_OFFICER,
    ROLE_DONOR_STAFF,
    ROLE_PHLEBOTOMIST,
    ROLE_LAB_TECHNICIAN,
    ROLE_LAB_INCHARGE,
    ROLE_ISSUE_STORE,
    ROLE_BILLING_STAFF,
    ROLE_VIEWER_AUDITOR,
]

# MFA (TOTP) is required for Admin and Medical Officer roles (Security section).
MFA_REQUIRED_ROLES: frozenset[str] = frozenset(
    {
        ROLE_SUPER_ADMIN,
        ROLE_BRANCH_ADMIN,
        ROLE_MEDICAL_OFFICER,
        ROLE_LAB_INCHARGE,
    }
)

_READ_ONLY: frozenset[str] = frozenset(
    {
        "branches:read",
        "masters:read",
        "settings:read",
        "barcodes:read",
    }
)

# Permission sets per role for Phase 1 (no donor/patient/blood actions yet).
ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    ROLE_SUPER_ADMIN: frozenset({"*"}),
    ROLE_BRANCH_ADMIN: frozenset(
        {
            "branches:read",
            "branches:update",
            "branches:switch",
            "users:create",
            "users:read",
            "users:update",
            "users:delete",
            "roles:read",
            "masters:create",
            "masters:read",
            "masters:update",
            "masters:delete",
            "settings:read",
            "settings:update",
            "audit:read",
            "barcodes:read",
        }
    ),
    ROLE_MEDICAL_OFFICER: frozenset(
        {
            "branches:read",
            "masters:read",
            "settings:read",
            "audit:read",
            "barcodes:read",
            "users:read",
        }
    ),
    ROLE_DONOR_STAFF: _READ_ONLY,
    ROLE_PHLEBOTOMIST: _READ_ONLY,
    ROLE_LAB_TECHNICIAN: _READ_ONLY,
    ROLE_LAB_INCHARGE: frozenset(
        {
            "branches:read",
            "masters:read",
            "settings:read",
            "audit:read",
            "barcodes:read",
        }
    ),
    ROLE_ISSUE_STORE: _READ_ONLY,
    ROLE_BILLING_STAFF: _READ_ONLY,
    ROLE_VIEWER_AUDITOR: frozenset(
        {
            "branches:read",
            "masters:read",
            "settings:read",
            "audit:read",
            "users:read",
            "roles:read",
            "barcodes:read",
        }
    ),
}


def role_has_permission(role_name: str, permission: str) -> bool:
    """True if the role is allowed the permission (Super Admin has all)."""
    perms = ROLE_PERMISSIONS.get(role_name)
    if perms is None:
        return False
    return "*" in perms or permission in perms


def role_requires_mfa(role_name: str) -> bool:
    return role_name in MFA_REQUIRED_ROLES
