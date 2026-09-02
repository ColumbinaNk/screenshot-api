"""Pydantic request/response schemas."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class ScreenshotFormat(str, Enum):
    png = "png"
    jpeg = "jpeg"


class ScreenshotRequest(BaseModel):
    url: str = Field(..., description="URL to screenshot", examples=["https://example.com"])
    width: int = Field(default=1280, ge=320, le=3840, description="Viewport width")
    height: int = Field(default=720, ge=320, le=2160, description="Viewport height")
    full_page: bool = Field(default=False, description="Capture full scrollable page")
    format: ScreenshotFormat = Field(default=ScreenshotFormat.png, description="Image format")
    quality: int = Field(default=80, ge=1, le=100, description="JPEG quality (1-100)")
    wait_ms: int = Field(default=0, ge=0, le=30000, description="Wait before capture (ms)")
    wait_selector: Optional[str] = Field(default=None, description="Wait for CSS selector")


class ScreenshotResponse(BaseModel):
    success: bool
    cached: bool = False
    width: int
    height: int
    format: str
    size_bytes: int
    duration_ms: float


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    browser: str
    uptime_s: float
    version: str
