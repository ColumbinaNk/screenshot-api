# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [1.0.0] — 2026-09-02

### Added
- Initial release
- `POST /v1/screenshot` — screenshot with JSON body
- `GET /v1/screenshot?url=` — screenshot with query params
- `GET /health` — browser status + uptime
- API key authentication (optional)
- SQLite rate limiter (persistent across restarts)
- File-based screenshot cache with configurable TTL
- Anti-detection browser via Camoufox (Firefox-based)
- Full-page and viewport screenshots
- PNG and JPEG output formats
- Custom viewport sizes (320-3840)
- Wait for CSS selector before capture
- Docker Compose single-service deployment
- Xvfb headed mode for stealth
