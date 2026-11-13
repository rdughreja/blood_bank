"""Rate limiting (slowapi, in-memory). Limits come from settings.

In tests (`settings.testing`), limits are raised to 10000/minute so the suite
is not flaky; the limiter itself is unit-tested with a low limit.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

_login_limit = (
    "10000/minute" if settings.testing else f"{settings.rate_limit_login_per_minute}/minute"
)
_auth_limit = (
    "10000/minute" if settings.testing else f"{settings.rate_limit_auth_per_minute}/minute"
)
_write_limit = (
    "10000/minute" if settings.testing else f"{settings.rate_limit_write_per_minute}/minute"
)

limiter = Limiter(key_func=get_remote_address, default_limits=[_write_limit])

LOGIN_LIMIT = _login_limit
AUTH_LIMIT = _auth_limit
WRITE_LIMIT = _write_limit
