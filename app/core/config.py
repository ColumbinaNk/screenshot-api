"""Application settings — all from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    # Server
    host: str = "0.0.0.0"
    port: int = int(os.getenv("PORT", "8000"))

    # Auth (empty = no auth)
    api_key: str = os.getenv("API_KEY", "")

    # Rate limit
    rate_limit: int = int(os.getenv("RATE_LIMIT", "60"))  # requests per minute per IP

    # Browser
    browser_timeout: int = int(os.getenv("BROWSER_TIMEOUT", "30"))  # seconds

    # Cache
    cache_dir: Path = Path(os.getenv("CACHE_DIR", "/data/cache"))
    cache_ttl: int = int(os.getenv("CACHE_TTL", "3600"))  # seconds
    cache_enabled: bool = os.getenv("CACHE_ENABLED", "true").lower() == "true"

    # Data dir (ratelimit db)
    data_dir: Path = Path(os.getenv("DATA_DIR", "/data"))

    # Screenshot defaults
    default_width: int = int(os.getenv("DEFAULT_WIDTH", "1280"))
    default_height: int = int(os.getenv("DEFAULT_HEIGHT", "720"))
    max_width: int = int(os.getenv("MAX_WIDTH", "3840"))
    max_height: int = int(os.getenv("MAX_HEIGHT", "2160"))

    def __post_init__(self) -> None:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
