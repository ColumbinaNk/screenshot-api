"""SQLite-based persistent rate limiter."""

from __future__ import annotations

import sqlite3
import time
from pathlib import Path

from app.core.config import settings


class RateLimiter:
    def __init__(self) -> None:
        self._db_path: Path = settings.data_dir / "ratelimit.db"
        self._conn: sqlite3.Connection | None = None

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(str(self._db_path), check_same_thread=False)
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS requests (
                    key TEXT NOT NULL,
                    timestamp INTEGER NOT NULL
                )
            """)
            self._conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_requests_key_ts
                ON requests (key, timestamp)
            """)
            self._conn.commit()
        return self._conn

    def is_rate_limited(self, key: str, limit: int, window_seconds: int = 60) -> bool:
        """Returns True if rate limit exceeded."""
        now = int(time.time())
        cutoff = now - window_seconds
        conn = self._get_conn()

        # Cleanup old entries (opportunistic)
        conn.execute("DELETE FROM requests WHERE timestamp < ?", (cutoff,))

        # Count current window
        count = conn.execute(
            "SELECT COUNT(*) FROM requests WHERE key = ? AND timestamp >= ?",
            (key, cutoff),
        ).fetchone()[0]

        if count >= limit:
            return True

        # Record this request
        conn.execute("INSERT INTO requests (key, timestamp) VALUES (?, ?)", (key, now))
        conn.commit()
        return False

    def get_usage(self, key: str, window_seconds: int = 60) -> int:
        """Get current request count for a key."""
        now = int(time.time())
        cutoff = now - window_seconds
        conn = self._get_conn()
        conn.execute("DELETE FROM requests WHERE timestamp < ?", (cutoff,))
        conn.commit()
        row = conn.execute(
            "SELECT COUNT(*) FROM requests WHERE key = ? AND timestamp >= ?",
            (key, cutoff),
        ).fetchone()
        return row[0] if row else 0

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None


rate_limiter = RateLimiter()
