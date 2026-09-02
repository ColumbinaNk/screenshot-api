"""Screenshot cache — file-based with hash keys."""

from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Optional

from app.core.config import settings


def _cache_key(url: str, width: int, height: int, full_page: bool, fmt: str, quality: int) -> str:
    """Deterministic cache key from request params."""
    raw = f"{url}|{width}|{height}|{full_page}|{fmt}|{quality}"
    return hashlib.sha256(raw.encode()).hexdigest()


def get_cached(url: str, width: int, height: int, full_page: bool, fmt: str, quality: int) -> Optional[bytes]:
    """Return cached screenshot bytes or None if miss/expired."""
    if not settings.cache_enabled:
        return None

    key = _cache_key(url, width, height, full_page, fmt, quality)
    cache_file = settings.cache_dir / f"{key}.{fmt}"

    if not cache_file.exists():
        return None

    # Check TTL
    age = time.time() - cache_file.stat().st_mtime
    if age > settings.cache_ttl:
        cache_file.unlink(missing_ok=True)
        return None

    return cache_file.read_bytes()


def save_cache(data: bytes, url: str, width: int, height: int, full_page: bool, fmt: str, quality: int) -> Path:
    """Save screenshot to cache. Returns file path."""
    key = _cache_key(url, width, height, full_page, fmt, quality)
    cache_file = settings.cache_dir / f"{key}.{fmt}"
    cache_file.write_bytes(data)
    return cache_file


def cleanup_expired() -> int:
    """Remove expired cache entries. Returns count removed."""
    if not settings.cache_enabled:
        return 0

    removed = 0
    now = time.time()
    for f in settings.cache_dir.iterdir():
        if f.is_file():
            age = now - f.stat().st_mtime
            if age > settings.cache_ttl:
                f.unlink()
                removed += 1
    return removed
