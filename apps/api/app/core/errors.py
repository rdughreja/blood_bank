"""Shared API error codes and the ApiError exception.

Every error the API returns uses the envelope in envelope.py. `code` values
are stable, uppercase, machine-readable strings from this module.
"""

from typing import Any


class ApiError(Exception):
    """An error that maps directly onto the API error envelope."""

    def __init__(
        self,
        status: int,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message
        self.details = details or {}


# Stable error codes (shared list, mirrored in the OpenAPI contract).
VALIDATION_ERROR = "VALIDATION_ERROR"
UNAUTHORIZED = "UNAUTHORIZED"
FORBIDDEN = "FORBIDDEN"
NOT_FOUND = "NOT_FOUND"
CONFLICT = "CONFLICT"
INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
ACCOUNT_LOCKED = "ACCOUNT_LOCKED"
ACCOUNT_INACTIVE = "ACCOUNT_INACTIVE"
MFA_REQUIRED = "MFA_REQUIRED"
MFA_INVALID = "MFA_INVALID"
TOKEN_EXPIRED = "TOKEN_EXPIRED"
TOKEN_INVALID = "TOKEN_INVALID"
RATE_LIMITED = "RATE_LIMITED"
INTERNAL_ERROR = "INTERNAL_ERROR"
