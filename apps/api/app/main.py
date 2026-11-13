"""FastAPI application factory — Blood Bank API, Phase 1 (Foundation).

Every response uses the envelope from BUILD_PLAN.md. No raw framework errors,
no HTML error pages, no bare strings leave this app.
"""

import logging
from collections.abc import AsyncIterator, Mapping
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core import errors
from app.core.config import settings
from app.core.envelope import utc_now_iso
from app.core.rate_limit import limiter
from app.core.security import new_request_id
from app.db.base import SessionLocal
from app.modules.audit.router import router as audit_router
from app.modules.auth.router import router as auth_router
from app.modules.barcodes.router import router as barcodes_router
from app.modules.branches.router import router as branches_router
from app.modules.masters.router import router as masters_router
from app.modules.settings.router import router as settings_router
from app.modules.users_roles.router import router as users_roles_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Blood Bank API starting (environment=%s)", settings.environment)
    yield
    logger.info("Blood Bank API stopping")


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", None) or new_request_id()


def _error_response(
    request: Request, status: int, code: str, message: str, details: Mapping[str, Any]
) -> JSONResponse:
    request_id = _request_id(request)
    return JSONResponse(
        status_code=status,
        content={
            "success": False,
            "error": {
                "code": code,
                "message": message,
                "details": details,
                "requestId": request_id,
                "timestamp": utc_now_iso(),
            },
        },
    )


def create_app() -> FastAPI:
    app = FastAPI(
        title="Blood Bank Web App API",
        description="Phase 1 (Foundation): auth, branches, users, masters, settings, audit.",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.state.limiter = limiter

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next: object) -> object:
        request.state.request_id = new_request_id()
        response = await call_next(request)  # type: ignore[operator]
        response.headers["X-Request-Id"] = request.state.request_id
        return response

    origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    @app.exception_handler(errors.ApiError)
    async def api_error_handler(request: Request, exc: errors.ApiError) -> JSONResponse:
        return _error_response(request, exc.status, exc.code, exc.message, exc.details)

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        details = {
            "fields": [
                {"field": ".".join(str(p) for p in err["loc"]), "message": err["msg"]}
                for err in exc.errors()
            ]
        }
        return _error_response(request, 400, errors.VALIDATION_ERROR, "Validation failed.", details)

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
        return _error_response(
            request, 429, errors.RATE_LIMITED, "Rate limit exceeded. Try again later.", {}
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        code = errors.NOT_FOUND if exc.status_code == 404 else errors.INTERNAL_ERROR
        message = exc.detail if isinstance(exc.detail, str) else "Not found."
        return _error_response(request, exc.status_code, code, message, {})

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error (requestId=%s)", _request_id(request))
        return _error_response(request, 500, errors.INTERNAL_ERROR, "Unexpected server error.", {})

    @app.get("/health")
    async def health(request: Request) -> dict[str, object]:
        return {
            "success": True,
            "data": {"status": "ok"},
            "meta": {"requestId": _request_id(request), "timestamp": utc_now_iso()},
        }

    @app.get("/health/db")
    async def health_db(request: Request) -> dict[str, object]:
        try:
            with SessionLocal() as db:
                db.execute(text("SELECT 1"))
            status = "ok"
        except Exception:
            logger.exception("Database health check failed")
            status = "error"
        return {
            "success": status == "ok",
            "data": {"status": status},
            "meta": {"requestId": _request_id(request), "timestamp": utc_now_iso()},
        }

    app.include_router(auth_router)
    app.include_router(branches_router)
    app.include_router(users_roles_router)
    app.include_router(masters_router)
    app.include_router(settings_router)
    app.include_router(audit_router)
    app.include_router(barcodes_router)
    return app


app = create_app()
