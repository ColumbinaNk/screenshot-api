"""Camoufox browser engine — embedded in the same process."""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Optional

from camoufox.async_api import AsyncCamoufox
from playwright.async_api import Browser, BrowserContext, Page

from app.core.config import settings

logger = logging.getLogger("browser")


class BrowserEngine:
    """Manages a single Camoufox browser instance for screenshots."""

    def __init__(self) -> None:
        self._cm: Optional[AsyncCamoufox] = None
        self._browser: Optional[Browser] = None
        self._started_at: float = 0.0

    async def start(self) -> None:
        """Launch browser. Called once on startup."""
        logger.info("Starting Camoufox browser...")
        self._cm = AsyncCamoufox(
            headless=False,  # headed + Xvfb for stealth
            geoip=False,
            humanize=False,
            persistent_context=False,
        )
        self._browser = await self._cm.__aenter__()
        self._started_at = time.time()
        logger.info("Browser ready")

    async def stop(self) -> None:
        """Close browser. Called on shutdown."""
        if self._cm:
            try:
                await self._cm.__aexit__(None, None, None)
                logger.info("Browser closed")
            except Exception as e:
                logger.warning(f"Browser close error: {e}")
        self._browser = None
        self._cm = None

    @property
    def is_running(self) -> bool:
        return self._browser is not None and self._browser.is_connected

    @property
    def uptime(self) -> float:
        if self._started_at <= 0:
            return 0.0
        return time.time() - self._started_at

    async def screenshot(
        self,
        url: str,
        width: int = 1280,
        height: int = 720,
        full_page: bool = False,
        wait_ms: int = 0,
        wait_selector: Optional[str] = None,
        img_format: str = "png",
        quality: int = 80,
        proxy: Optional[str] = None,
    ) -> tuple[bytes, float]:
        """
        Take a screenshot of the given URL.
        Returns (image_bytes, duration_ms).
        """
        if not self.is_running:
            raise RuntimeError("Browser not running")

        context: Optional[BrowserContext] = None
        page: Optional[Page] = None
        start = time.monotonic()

        try:
            # Resolve proxy: per-request override > global env
            proxy_url = proxy or settings.proxy or None
            context_kwargs: dict = {
                "viewport": {"width": width, "height": height},
            }
            if proxy_url:
                context_kwargs["proxy"] = {"server": proxy_url}

            context = await self._browser.new_context(**context_kwargs)
            page = await context.new_page()

            # Block media/fonts to speed up loading
            await page.route(
                "**/*.{png,jpg,jpeg,gif,webp,svg,ico,woff,woff2,ttf,otf,eot}",
                lambda route: route.abort(),
            )

            # Navigate
            await page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=settings.browser_timeout * 1000,
            )

            # Wait for specific element if requested
            if wait_selector:
                try:
                    await page.wait_for_selector(
                        wait_selector, timeout=min(wait_ms, 10000) or 5000
                    )
                except Exception:
                    logger.warning(
                        f"Selector '{wait_selector}' not found, capturing anyway"
                    )

            # Extra wait
            if wait_ms > 0 and not wait_selector:
                await asyncio.sleep(wait_ms / 1000)

            # Capture
            screenshot_kwargs: dict = {"full_page": full_page}
            if img_format == "jpeg":
                screenshot_kwargs["type"] = "jpeg"
                screenshot_kwargs["quality"] = quality
            else:
                screenshot_kwargs["type"] = "png"

            img_bytes = await page.screenshot(**screenshot_kwargs)
            duration = (time.monotonic() - start) * 1000

            logger.info(
                f"Screenshot OK: {url} ({len(img_bytes)} bytes, {duration:.0f}ms)"
            )
            return img_bytes, duration

        except Exception as e:
            duration = (time.monotonic() - start) * 1000
            logger.error(f"Screenshot FAIL: {url} ({duration:.0f}ms) — {e}")
            raise

        finally:
            if page:
                try:
                    await page.close()
                except Exception:
                    pass
            if context:
                try:
                    await context.close()
                except Exception:
                    pass


# Global singleton
browser_engine = BrowserEngine()
