"""Response envelope — the exact contract from BUILD_PLAN.md.

Success (single item):
  {"success": true, "data": {...}, "meta": {"requestId": ..., "timestamp": ...}}
Success (list, always paginated):
  {"success": true, "data": [...], "meta": {requestId, timestamp, page,
   pageSize, total, totalPages}}
Error:
  {"success": false, "error": {"code", "message", "details", "requestId",
   "timestamp"}}
"""

from datetime import UTC, datetime
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field, PlainSerializer


def _format_utc(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.isoformat().replace("+00:00", "Z")


UtcDateTime = Annotated[datetime, PlainSerializer(_format_utc, return_type=str | None)]


def utc_now_iso() -> str:
    """Current UTC time as an ISO 8601 string ending in Z."""
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


class Meta(BaseModel):
    """Response metadata. Pagination fields are present only on list responses.

    Serialized with the plan's camelCase names (requestId, pageSize, totalPages).
    """

    model_config = ConfigDict(populate_by_name=True)

    request_id: str = Field(serialization_alias="requestId")
    timestamp: str
    page: int | None = None
    page_size: int | None = Field(default=None, serialization_alias="pageSize")
    total: int | None = None
    total_pages: int | None = Field(default=None, serialization_alias="totalPages")


class SuccessEnvelope[T](BaseModel):
    success: bool = True
    data: T
    meta: Meta


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = {}
    request_id: str
    timestamp: str


class ErrorEnvelope(BaseModel):
    success: bool = False
    error: ErrorDetail


def make_meta(request_id: str) -> Meta:
    return Meta(request_id=request_id, timestamp=utc_now_iso())


def make_page_meta(request_id: str, page: int, page_size: int, total: int) -> Meta:
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return Meta(
        request_id=request_id,
        timestamp=utc_now_iso(),
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
    )


def paginate_params(page: int, page_size: int) -> tuple[int, int]:
    """Clamp list pagination to the plan contract: default 20, max 100."""
    page = max(1, page)
    page_size = min(max(1, page_size), 100)
    return page, page_size
