"""Column-level encryption for contact details (Security section, Phase 1).

- `EncryptedString` is a SQLAlchemy type that encrypts on write and decrypts
  on read (Fernet, AES-128-CBC + HMAC).
- `blind_index()` is an HMAC of a value used for lookups on encrypted
  columns (e.g. login by email) without decrypting every row.

Keys: `ENCRYPTION_KEY` env var holds a Fernet key. If it is not set, a key is
derived from `SECRET_KEY` — acceptable only for local development; production
must set a dedicated key.
"""

import base64
import hashlib
import hmac
import logging

from cryptography.fernet import Fernet
from sqlalchemy import String
from sqlalchemy.types import TypeDecorator

from app.core.config import settings

logger = logging.getLogger(__name__)

_fernet: Fernet | None = None


def _derive_dev_key() -> bytes:
    digest = hashlib.sha256(f"blood-bank-dev-key:{settings.secret_key}".encode()).digest()
    return base64.urlsafe_b64encode(digest)


def get_fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        key = settings.encryption_key or ""
        if not key:
            logger.warning(
                "ENCRYPTION_KEY is not set; deriving a development-only key "
                "from SECRET_KEY. Set a dedicated ENCRYPTION_KEY in production."
            )
            _fernet = Fernet(_derive_dev_key())
        else:
            _fernet = Fernet(key.encode("utf-8"))
    return _fernet


def encrypt_str(value: str | None) -> str | None:
    if value is None:
        return None
    return get_fernet().encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_str(value: str | None) -> str | None:
    if value is None:
        return None
    return get_fernet().decrypt(value.encode("utf-8")).decode("utf-8")


def blind_index(value: str) -> str:
    """Deterministic HMAC hex used to look up a row by an encrypted value."""
    return hmac.new(
        settings.secret_key.encode("utf-8"), value.strip().lower().encode("utf-8"), hashlib.sha256
    ).hexdigest()


class EncryptedString(TypeDecorator[str]):
    """A string column stored encrypted at rest (Fernet)."""

    impl = String
    cache_ok = True

    def process_bind_param(self, value: str | None, dialect: object) -> str | None:
        if value is None:
            return None
        return encrypt_str(value)

    def process_result_value(self, value: str | None, dialect: object) -> str | None:
        if value is None:
            return None
        return decrypt_str(value)
