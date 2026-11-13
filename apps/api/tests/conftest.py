"""Pytest fixtures — PostgreSQL test database, seeded demo data, API client.

Requires a local PostgreSQL server with a `bloodbank` superuser (see README).
The test database is `bloodbank_test`; it is dropped and recreated per session.
"""

import os

os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = (
    "postgresql+psycopg://bloodbank:bloodbank_dev@localhost:5432/bloodbank_test"
)
os.environ["SECRET_KEY"] = "test-secret-key-for-pytest-only"
os.environ["ENCRYPTION_KEY"] = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="

import pyotp  # noqa: E402
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine, text  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.db.base import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402

TEST_DATABASE_URL = settings.database_url
ADMIN_URL = "postgresql+psycopg://bloodbank:bloodbank_dev@localhost:5432/postgres"

DEMO_PASSWORD = "Demo@123456"


@pytest.fixture(scope="session")
def engine():
    """Create the test database and tables once per session."""
    admin_engine = create_engine(ADMIN_URL, isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = 'bloodbank_test'")
        ).scalar_one_or_none()
        if exists is None:
            conn.execute(text("CREATE DATABASE bloodbank_test"))
    admin_engine.dispose()
    test_engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    # Seed demo data (roles, masters, settings, branches, users, donors).
    import seed as seed_module

    seed_module.seed()
    yield test_engine
    test_engine.dispose()


@pytest.fixture
def db(engine):
    """One transactional session per test — rolled back afterwards."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db):
    """TestClient with get_db overridden to the test transaction."""

    def _override_db():
        yield db

    app.dependency_overrides[get_db] = _override_db
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def login(client: TestClient, email: str, password: str) -> dict[str, str]:
    """Log in and return Authorization headers (handles MFA roles)."""
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    data = response.json()["data"]
    if data.get("mfa_required"):
        mfa_token = data["mfa_token"]
        setup = client.post("/auth/mfa/setup", headers={"Authorization": f"Bearer {mfa_token}"})
        assert setup.status_code == 200, setup.text
        secret = setup.json()["data"]["secret"]
        code = pyotp.TOTP(secret).now()
        confirm = client.post(
            "/auth/mfa/confirm",
            json={"code": code},
            headers={"Authorization": f"Bearer {mfa_token}"},
        )
        assert confirm.status_code == 200, confirm.text
        tokens = confirm.json()["data"]
    else:
        tokens = data
    return {"Authorization": f"Bearer {tokens['access_token']}"}


@pytest.fixture
def admin_headers(client):
    return login(client, settings.seed_admin_email, settings.seed_admin_password)


@pytest.fixture
def branch_admin_headers(client):
    return login(client, "branch.admin@demo.local", DEMO_PASSWORD)


@pytest.fixture
def donor_staff_headers(client):
    return login(client, "donor.staff@demo.local", DEMO_PASSWORD)


@pytest.fixture
def auditor_headers(client):
    return login(client, "auditor@demo.local", DEMO_PASSWORD)


@pytest.fixture
def medical_officer_headers(client):
    return login(client, "medical.officer@demo.local", DEMO_PASSWORD)
