"""Screenshot API — main application entry point."""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.auth import AuthMiddleware
from app.core.browser import browser_engine
from app.core.config import settings
from app.core.ratelimit import rate_limiter
from app.routes.screenshot import router as screenshot_router

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start browser on startup, cleanup on shutdown."""
    # Start Xvfb if not already running
    if not os.environ.get("DISPLAY"):
        logger.info("Starting Xvfb...")
        os.system("Xvfb :99 -screen 0 1280x1024x24 -nolisten tcp &")
        os.environ["DISPLAY"] = ":99"
        import time
        time.sleep(2)

    await browser_engine.start()
    logger.info(f"Screenshot API ready on port {settings.port}")
    yield
    await browser_engine.stop()
    rate_limiter.close()
    logger.info("Shutdown complete")


app = FastAPI(
    title="Screenshot API",
    description="Self-hosted web screenshot API powered by Camoufox",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Middleware
app.add_middleware(AuthMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(screenshot_router)


@app.get("/")
async def root():
    return {
        "name": "screenshot-api",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "POST /v1/screenshot": "Screenshot with JSON body",
            "GET /v1/screenshot?url=": "Screenshot with query params",
            "GET /health": "Health check",
        },
    }
