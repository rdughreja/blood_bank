"""Seed script — FAKE demo data only. Never run with real people's data.

Seeds: all roles + permissions, master defaults, settings defaults (clinical
values labelled "confirm with Medical Officer"), 3 demo branches, one Super
Admin, one demo user per role, 200 fake donors and 5 sample camps.
Idempotent: re-running skips already-seeded rows.
"""

import random
import sys
from datetime import date, timedelta

from faker import Faker
from sqlalchemy import select

sys.path.insert(0, ".")
from app.core.config import settings  # noqa: E402
from app.core.crypto import blind_index  # noqa: E402
from app.core.rbac import ALL_ROLES, ROLE_PERMISSIONS  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.db.base import Base, SessionLocal, engine  # noqa: E402
from app.modules.branches.models import Branch  # noqa: E402
from app.modules.masters.models import MasterData  # noqa: E402
from app.modules.seed_data.models import SeedCamp, SeedDonor  # noqa: E402
from app.modules.settings.models import Setting  # noqa: E402
from app.modules.users_roles.models import (  # noqa: E402
    Permission,
    Role,
    RolePermission,
    User,
    UserBranch,
)

fake = Faker("en_IN")
random.seed(42)
Faker.seed(42)

SETTING_DEFAULTS: list[dict[str, object]] = [
    {
        "key": "eligibility.min_age",
        "value": 18,
        "label": "Minimum donor age (years)",
        "confirm_with_mo": True,
    },
    {
        "key": "eligibility.max_age",
        "value": 65,
        "label": "Maximum donor age (years)",
        "confirm_with_mo": True,
    },
    {
        "key": "eligibility.min_weight_kg",
        "value": 50,
        "label": "Minimum donor weight (kg)",
        "confirm_with_mo": True,
    },
    {
        "key": "eligibility.min_hb_g_dl",
        "value": 12.5,
        "label": "Minimum haemoglobin (g/dL)",
        "description": "Clinical-conflict flag: one source states 11.5 for female donors. Confirm with Medical Officer.",
        "confirm_with_mo": True,
    },
    {
        "key": "eligibility.min_hb_female_g_dl",
        "value": 11.5,
        "label": "Minimum haemoglobin, female donors (g/dL)",
        "description": "Alternative value from a second source. Confirm with Medical Officer.",
        "confirm_with_mo": True,
    },
    {
        "key": "donation_gap.whole_blood_months",
        "value": 3,
        "label": "Minimum gap, whole blood (months)",
        "confirm_with_mo": True,
    },
    {
        "key": "donation_gap.platelet_apheresis_hours",
        "value": 48,
        "label": "Minimum gap, platelet apheresis (hours)",
        "confirm_with_mo": True,
    },
    {
        "key": "donation_gap.plasma_apheresis_weeks",
        "value": 2,
        "label": "Minimum gap, plasma apheresis (weeks)",
        "confirm_with_mo": True,
    },
    {
        "key": "shelf_life.wb_prbc_days",
        "value": 35,
        "label": "Shelf life, whole blood / PRBC (days)",
        "confirm_with_mo": True,
    },
    {
        "key": "shelf_life.ffp_cryo_days",
        "value": 365,
        "label": "Shelf life, FFP / cryoprecipitate (days)",
        "confirm_with_mo": True,
    },
    {
        "key": "shelf_life.platelets_sdp_days",
        "value": 5,
        "label": "Shelf life, platelets / SDP (days)",
        "confirm_with_mo": True,
    },
    {
        "key": "crossmatch.hold_hours",
        "value": 72,
        "label": "Crossmatch allocation hold (hours)",
        "confirm_with_mo": True,
    },
    {
        "key": "alerts.expiry_warning_days",
        "value": 7,
        "label": "Expiring-soon alert threshold (days)",
        "confirm_with_mo": False,
    },
    {
        "key": "security.lockout_threshold",
        "value": 5,
        "label": "Failed logins before lockout",
        "confirm_with_mo": False,
    },
    {
        "key": "security.lockout_minutes",
        "value": 15,
        "label": "Account lockout duration (minutes)",
        "confirm_with_mo": False,
    },
    {
        "key": "dpdp.consent_required",
        "value": True,
        "label": "Donor consent required at registration",
        "confirm_with_mo": False,
    },
    {
        "key": "dpdp.retention_years",
        "value": 5,
        "label": "Record retention (years)",
        "confirm_with_mo": False,
    },
]

MASTER_DEFAULTS: list[tuple[str, str, str, dict[str, object] | None]] = [
    ("blood_group", "O-", "O Negative", None),
    ("blood_group", "O+", "O Positive", None),
    ("blood_group", "A-", "A Negative", None),
    ("blood_group", "A+", "A Positive", None),
    ("blood_group", "B-", "B Negative", None),
    ("blood_group", "B+", "B Positive", None),
    ("blood_group", "AB-", "AB Negative", None),
    ("blood_group", "AB+", "AB Positive", None),
    ("component_type", "WB", "Whole Blood", None),
    ("component_type", "PRBC", "Packed Red Blood Cells", None),
    ("component_type", "FFP", "Fresh Frozen Plasma", None),
    ("component_type", "PLT", "Platelets", None),
    ("component_type", "CRYO", "Cryoprecipitate", None),
    ("component_type", "SDP", "Single Donor Platelets", None),
    ("test_name", "HIV", "HIV 1 & 2", None),
    ("test_name", "HBSAG", "Hepatitis B (HBsAg)", None),
    ("test_name", "HCV", "Hepatitis C (Anti-HCV)", None),
    ("test_name", "SYPH", "Syphilis (VDRL/RPR)", None),
    ("test_name", "MAL", "Malaria", None),
    ("deferral_reason", "LOW_HB", "Low haemoglobin", None),
    ("deferral_reason", "LOW_WEIGHT", "Underweight", None),
    ("deferral_reason", "FEVER", "Fever / infection", None),
    ("deferral_reason", "RECENT_DONATION", "Donated too recently", None),
    ("deferral_reason", "MEDICATION", "Medication", None),
    ("deferral_reason", "TRAVEL", "Travel to endemic area", None),
    ("deferral_reason", "OTHER", "Other", None),
    ("discard_reason", "EXPIRED", "Expired", None),
    ("discard_reason", "REACTIVE_TTI", "Reactive TTI test", None),
    ("discard_reason", "DAMAGED_BAG", "Damaged bag", None),
    ("discard_reason", "CONTAMINATION", "Contamination", None),
    ("discard_reason", "OTHER", "Other", None),
    ("hospital", "DEMO-GENERAL", "Demo General Hospital", None),
    ("hospital", "DEMO-CITY", "Demo City Hospital", None),
    ("hospital", "DEMO-MEDICAL", "Demo Medical College Hospital", None),
    ("ward", "WARD-A", "Ward A", None),
    ("ward", "WARD-B", "Ward B", None),
    ("ward", "ICU", "ICU", None),
    ("ward", "EMERGENCY", "Emergency", None),
    ("charge", "CHG-PRBC", "PRBC unit charge", {"amount_paise": 150000}),
    ("charge", "CHG-FFP", "FFP unit charge", {"amount_paise": 100000}),
    ("charge", "CHG-PLT", "Platelet unit charge", {"amount_paise": 200000}),
    ("charge", "CHG-WB", "Whole blood unit charge", {"amount_paise": 120000}),
    ("charge", "CHG-XMATCH", "Crossmatch charge", {"amount_paise": 50000}),
    ("charge", "CHG-REG", "Registration charge", {"amount_paise": 0}),
]

BRANCHES: list[dict[str, object]] = [
    {
        "code": "MB-01",
        "name": "Morbi Main Centre",
        "address": "Demo Road, Morbi, Gujarat",
        "licence_no": "DEMO-LIC-001",
        "is_storage_centre": True,
    },
    {
        "code": "RJ-01",
        "name": "Rajkot Centre",
        "address": "Demo Road, Rajkot, Gujarat",
        "licence_no": "DEMO-LIC-002",
        "is_storage_centre": False,
    },
    {
        "code": "AH-01",
        "name": "Ahmedabad Centre",
        "address": "Demo Road, Ahmedabad, Gujarat",
        "licence_no": "DEMO-LIC-003",
        "is_storage_centre": False,
    },
]

DEMO_USERS: list[tuple[str, str, str]] = [
    ("Super Admin", "super.admin@demo.local", "Super Admin (Demo)"),
    ("Branch Admin", "branch.admin@demo.local", "Branch Admin (Demo)"),
    ("Medical Officer", "medical.officer@demo.local", "Medical Officer (Demo)"),
    ("Donor Staff / Counsellor", "donor.staff@demo.local", "Donor Staff (Demo)"),
    ("Phlebotomist / Collection Staff", "phlebotomist@demo.local", "Phlebotomist (Demo)"),
    ("Lab Technician", "lab.technician@demo.local", "Lab Technician (Demo)"),
    ("Lab In-charge", "lab.incharge@demo.local", "Lab In-charge (Demo)"),
    ("Issue / Store Staff", "issue.store@demo.local", "Issue Store Staff (Demo)"),
    ("Billing Staff", "billing.staff@demo.local", "Billing Staff (Demo)"),
    ("Viewer / Auditor", "auditor@demo.local", "Auditor (Demo)"),
]

DEMO_PASSWORD = "Demo@123456"
BLOOD_GROUPS = ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"]


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # --- Roles + permissions ---
        roles: dict[str, Role] = {}
        for role_name in ALL_ROLES:
            role = db.execute(select(Role).where(Role.name == role_name)).scalar_one_or_none()
            if role is None:
                role = Role(name=role_name, description=f"{role_name} role (Phase 1 seed)")
                db.add(role)
                db.flush()
            roles[role_name] = role
        all_permissions: set[str] = set()
        for perms in ROLE_PERMISSIONS.values():
            all_permissions.update(perms)
        all_permissions.discard("*")
        perm_rows: dict[str, Permission] = {}
        for perm_name in sorted(all_permissions):
            resource, _, action = perm_name.partition(":")
            perm = db.execute(
                select(Permission).where(Permission.name == perm_name)
            ).scalar_one_or_none()
            if perm is None:
                perm = Permission(name=perm_name, resource=resource, action=action)
                db.add(perm)
                db.flush()
            perm_rows[perm_name] = perm
        for role_name, perms in ROLE_PERMISSIONS.items():
            wanted = set(all_permissions) if "*" in perms else set(perms)
            for perm_name in wanted:
                exists = db.execute(
                    select(RolePermission).where(
                        RolePermission.role_id == roles[role_name].id,
                        RolePermission.permission_id == perm_rows[perm_name].id,
                    )
                ).scalar_one_or_none()
                if exists is None:
                    db.add(
                        RolePermission(
                            role_id=roles[role_name].id, permission_id=perm_rows[perm_name].id
                        )
                    )
        db.commit()
        print(f"Seeded {len(roles)} roles, {len(perm_rows)} permissions.")

        # --- Settings defaults ---
        for item in SETTING_DEFAULTS:
            existing = db.execute(
                select(Setting).where(Setting.key == item["key"], Setting.scope == "global")
            ).scalar_one_or_none()
            if existing is None:
                db.add(
                    Setting(
                        key=str(item["key"]),
                        value=item["value"],
                        scope="global",
                        branch_id=None,
                        confirm_with_mo=bool(item.get("confirm_with_mo", False)),
                        label=str(item.get("label", "")),
                        description=str(item.get("description", "")) or None,
                    )
                )
        db.commit()
        print(f"Seeded {len(SETTING_DEFAULTS)} global settings.")

        # --- Masters ---
        for mtype, code, name, extra in MASTER_DEFAULTS:
            existing_master = db.execute(
                select(MasterData).where(
                    MasterData.type == mtype,
                    MasterData.code == code,
                    MasterData.branch_id.is_(None),
                )
            ).scalar_one_or_none()
            if existing_master is None:
                db.add(MasterData(type=mtype, code=code, name=name, extra=extra, branch_id=None))
        db.commit()
        print(f"Seeded {len(MASTER_DEFAULTS)} master records.")

        # --- Branches ---
        branches: dict[str, Branch] = {}
        for b in BRANCHES:
            branch = db.execute(select(Branch).where(Branch.code == b["code"])).scalar_one_or_none()
            if branch is None:
                branch = Branch(
                    code=str(b["code"]),
                    name=str(b["name"]),
                    address=str(b["address"]),
                    licence_no=str(b["licence_no"]),
                    is_storage_centre=bool(b["is_storage_centre"]),
                )
                db.add(branch)
                db.flush()
            branches[str(b["code"])] = branch
        db.commit()
        print(f"Seeded {len(branches)} branches.")

        # --- Super Admin ---
        admin_email = settings.seed_admin_email
        admin = db.execute(
            select(User).where(User.email_lookup == blind_index(admin_email))
        ).scalar_one_or_none()
        if admin is None:
            admin = User(
                email=admin_email,
                email_lookup=blind_index(admin_email),
                mobile="9000000001",
                full_name="Super Admin",
                password_hash=hash_password(settings.seed_admin_password),
                role_id=roles["Super Admin"].id,
            )
            db.add(admin)
            db.flush()
            for i, branch in enumerate(branches.values()):
                db.add(UserBranch(user_id=admin.id, branch_id=branch.id, is_primary=(i == 0)))
            db.commit()
            print(f"Created Super Admin {admin_email}.")
        else:
            print("Super Admin already exists; skipped.")

        # --- Demo user per role (fake data only) ---
        for role_name, email, full_name in DEMO_USERS:
            existing_user = db.execute(
                select(User).where(User.email_lookup == blind_index(email))
            ).scalar_one_or_none()
            if existing_user is not None:
                continue
            user = User(
                email=email,
                email_lookup=blind_index(email),
                mobile=f"90000000{10 + len(email) % 80:02d}",
                full_name=full_name,
                password_hash=hash_password(DEMO_PASSWORD),
                role_id=roles[role_name].id,
            )
            db.add(user)
            db.flush()
            db.add(UserBranch(user_id=user.id, branch_id=branches["MB-01"].id, is_primary=True))
            db.commit()
        print(f"Demo users ensured (password for all demo users: {DEMO_PASSWORD}).")

        # --- 200 fake donors (demo data only) ---
        existing_donors = db.execute(select(SeedDonor)).scalars().all()
        if len(existing_donors) < 200:
            branch_ids = list(branches.values())
            for i in range(len(existing_donors), 200):
                dob = fake.date_of_birth(minimum_age=18, maximum_age=65)
                donor = SeedDonor(
                    donor_code=f"DN-{i + 1:05d}",
                    full_name=fake.name(),
                    date_of_birth=dob,
                    gender=random.choice(["Male", "Female", "Other"]),
                    blood_group=random.choice(BLOOD_GROUPS),
                    mobile=f"9{random.randint(100000000, 999999999)}",
                    email=f"donor{i + 1:03d}@demo.local",
                    branch_id=random.choice(branch_ids).id,
                )
                db.add(donor)
            db.commit()
        print("Seeded 200 fake donors.")

        # --- Sample camps ---
        existing_camps = db.execute(select(SeedCamp)).scalars().all()
        if not existing_camps:
            camp_names = [
                (
                    "Blood Donation Camp — Demo College",
                    "Demo College NSS",
                    "Demo College Campus, Morbi",
                ),
                (
                    "Blood Donation Camp — Demo Rotary",
                    "Demo Rotary Club",
                    "Demo Community Hall, Rajkot",
                ),
                (
                    "Blood Donation Camp — Demo Factory",
                    "Demo Industries",
                    "Demo Factory Premises, Ahmedabad",
                ),
                (
                    "Blood Donation Camp — Demo School",
                    "Demo School Trust",
                    "Demo School Ground, Morbi",
                ),
                (
                    "Blood Donation Camp — Demo Temple Trust",
                    "Demo Temple Trust",
                    "Demo Temple Hall, Rajkot",
                ),
            ]
            for j, (name, org, venue) in enumerate(camp_names):
                db.add(
                    SeedCamp(
                        name=name,
                        organizer=org,
                        venue=venue,
                        camp_date=date.today() + timedelta(days=7 + j * 5),
                        target_units=50 + j * 10,
                        branch_id=list(branches.values())[j % 3].id,
                        status="planned",
                    )
                )
            db.commit()
        print("Seeded 5 sample camps.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
    print("Seed complete.")
