"""API key authentication middleware."""

from __future__ import annotations

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings

# Endpoints that don't require auth
PUBLIC_PATHS = {"/", "/health", "/docs", "/openapi.json", "/redoc"}


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip auth for public paths
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        # Skip if no API key configured
        if not settings.api_key:
            return await call_next(request)

        # Check API key
        api_key = request.headers.get("x-api-key") or ""
        if not api_key:
            # Also check Authorization: Bearer ***
            auth = request.headers.get("authorization", "")
            if auth.startswith("Bearer "):
                api_key = auth[7:]

        if api_key != settings.api_key:
            raise HTTPException(status_code=401, detail="Invalid or missing API key")

        return await call_next(request)
