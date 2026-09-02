"""Screenshot endpoints."""

from __future__ import annotations

import time

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import JSONResponse

from app.core.browser import browser_engine
from app.core.config import settings
from app.core.ratelimit import rate_limiter
from app.models.schemas import (
    ErrorResponse,
    HealthResponse,
    ScreenshotFormat,
    ScreenshotRequest,
    ScreenshotResponse,
)
from app.utils.cache import get_cached, save_cache

router = APIRouter(tags=["screenshot"])


def _get_client_ip(request: Request) -> str:
    """Extract real IP (supports reverse proxy)."""
    return (
        request.headers.get("cf-connecting-ip")
        or request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        or (request.client.host if request.client else "unknown")
    )


@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok" if browser_engine.is_running else "degraded",
        browser="camoufox" if browser_engine.is_running else "down",
        uptime_s=round(browser_engine.uptime, 1),
        version="1.0.0",
    )


@router.post(
    "/v1/screenshot",
    response_model=ScreenshotResponse,
    responses={400: {"model": ErrorResponse}, 429: {"model": ErrorResponse}},
)
async def screenshot_post(req: ScreenshotRequest, request: Request):
    return await _take_screenshot(req, request)


@router.get(
    "/v1/screenshot",
    response_model=ScreenshotResponse,
    responses={400: {"model": ErrorResponse}, 429: {"model": ErrorResponse}},
)
async def screenshot_get(
    request: Request,
    url: str,
    width: int = 1280,
    height: int = 720,
    full_page: bool = False,
    format: ScreenshotFormat = ScreenshotFormat.png,
    quality: int = 80,
    wait_ms: int = 0,
    wait_selector: str | None = None,
):
    req = ScreenshotRequest(
        url=url,
        width=width,
        height=height,
        full_page=full_page,
        format=format,
        quality=quality,
        wait_ms=wait_ms,
        wait_selector=wait_selector,
    )
    return await _take_screenshot(req, request)


async def _take_screenshot(req: ScreenshotRequest, http_request: Request) -> Response:
    # Rate limit check
    client_ip = _get_client_ip(http_request)
    if rate_limiter.is_rate_limited(client_ip, settings.rate_limit):
        usage = rate_limiter.get_usage(client_ip)
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded ({usage}/{settings.rate_limit} per minute)",
            headers={"Retry-After": "60"},
        )

    # Cache check
    cached = get_cached(req.url, req.width, req.height, req.full_page, req.format.value, req.quality)
    if cached is not None:
        return Response(
            content=cached,
            media_type=f"image/{req.format.value}",
            headers={
                "X-Cache": "HIT",
                "Content-Disposition": f'inline; filename="screenshot.{req.format.value}"',
            },
        )

    # Take screenshot
    if not browser_engine.is_running:
        raise HTTPException(status_code=503, detail="Browser not available")

    start = time.monotonic()
    try:
        img_bytes, duration_ms = await browser_engine.screenshot(
            url=req.url,
            width=req.width,
            height=req.height,
            full_page=req.full_page,
            wait_ms=req.wait_ms,
            wait_selector=req.wait_selector,
            img_format=req.format.value,
            quality=req.quality,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Screenshot failed: {str(e)}")

    # Save to cache
    save_cache(img_bytes, req.url, req.width, req.height, req.full_page, req.format.value, req.quality)

    return Response(
        content=img_bytes,
        media_type=f"image/{req.format.value}",
        headers={
            "X-Cache": "MISS",
            "X-Screenshot-Duration-Ms": str(int(duration_ms)),
            "Content-Disposition": f'inline; filename="screenshot.{req.format.value}"',
        },
    )
