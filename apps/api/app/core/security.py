"""Security helpers: password hashing (argon2), JWT, TOTP (MFA), password policy."""

import hashlib
import re
import secrets
import uuid
from datetime import UTC, datetime, timedelta

import jwt
import pyotp
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.core.config import settings

_hasher = PasswordHasher()

# Password policy — see docs/decisions.md (plan defines no values).
PASSWORD_MIN_LENGTH = 12
_PASSWORD_UPPER = re.compile(r"[A-Z]")
_PASSWORD_LOWER = re.compile(r"[a-z]")
_PASSWORD_DIGIT = re.compile(r"[0-9]")
_PASSWORD_SPECIAL = re.compile(r"[^A-Za-z0-9]")


def validate_password_policy(password: str) -> list[str]:
    """Return a list of policy violations (empty = password is acceptable)."""
    violations: list[str] = []
    if len(password) < PASSWORD_MIN_LENGTH:
        violations.append(f"Password must be at least {PASSWORD_MIN_LENGTH} characters.")
    if not _PASSWORD_UPPER.search(password):
        violations.append("Password must contain an uppercase letter.")
    if not _PASSWORD_LOWER.search(password):
        violations.append("Password must contain a lowercase letter.")
    if not _PASSWORD_DIGIT.search(password):
        violations.append("Password must contain a digit.")
    if not _PASSWORD_SPECIAL.search(password):
        violations.append("Password must contain a special character.")
    return violations


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bool(_hasher.verify(password_hash, password))
    except VerifyMismatchError:
        return False
    except Exception:
        return False


def _utcnow() -> datetime:
    return datetime.now(UTC)


def create_access_token(
    user_id: str,
    email: str,
    role: str,
    branch_id: str | None,
    branches: list[str],
    expires_minutes: int | None = None,
) -> str:
    now = _utcnow()
    expires = now + timedelta(minutes=expires_minutes or settings.access_token_expire_minutes)
    payload: dict[str, object] = {
        "sub": user_id,
        "email": email,
        "role": role,
        "branch_id": branch_id,
        "branches": branches,
        "type": "access",
        "jti": str(uuid.uuid4()),
        "iat": now,
        "exp": expires,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(user_id: str) -> tuple[str, str]:
    """Return (token, jti). The jti is stored hashed server-side."""
    jti = str(uuid.uuid4())
    now = _utcnow()
    expires = now + timedelta(days=settings.refresh_token_expire_days)
    payload: dict[str, object] = {
        "sub": user_id,
        "type": "refresh",
        "jti": jti,
        "iat": now,
        "exp": expires,
    }
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)
    return token, jti


def create_mfa_token(user_id: str) -> str:
    now = _utcnow()
    expires = now + timedelta(minutes=settings.mfa_token_expire_minutes)
    payload: dict[str, object] = {
        "sub": user_id,
        "type": "mfa",
        "jti": str(uuid.uuid4()),
        "iat": now,
        "exp": expires,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str, expected_type: str) -> dict[str, object]:
    """Decode and validate a JWT; raises jwt.PyJWTError on any problem."""
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    if payload.get("type") != expected_type:
        raise jwt.InvalidTokenError(f"Expected a {expected_type} token.")
    return dict(payload)


def hash_token(token: str) -> str:
    """SHA-256 of a token, for server-side storage (never store raw tokens)."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generate_totp_secret() -> str:
    return pyotp.random_base32()


def totp_provisioning_uri(secret: str, email: str, issuer: str = "BloodBank") -> str:
    return pyotp.TOTP(secret).provisioning_uri(name=email, issuer_name=issuer)


def verify_totp(secret: str, code: str) -> bool:
    totp = pyotp.TOTP(secret)
    # valid_window=1 tolerates one 30-second step of clock skew.
    return bool(totp.verify(code, valid_window=1))


def new_request_id() -> str:
    return f"req_{secrets.token_hex(12)}"


def random_code(length: int = 6) -> str:
    alphabet = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"  # Crockford base32, no 0/O/1/I/L
    return "".join(secrets.choice(alphabet) for _ in range(length))
