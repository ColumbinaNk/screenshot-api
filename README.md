# Screenshot API

Self-hosted web screenshot API powered by [Camoufox](https://camoufox.com/) — a Firefox-based anti-detection browser.

## Features

- **Full-page & viewport screenshots** — PNG or JPEG output
- **Anti-detection** — Camoufox with real Firefox fingerprint
- **Docker-ready** — single `docker compose up`, no extra services
- **API key auth** — optional, for protecting your instance
- **Rate limiting** — per-IP, SQLite-backed (persists across restarts)
- **Screenshot cache** — file-based with configurable TTL
- **OpenAPI docs** — auto-generated at `/docs`

## Quick Start

```bash
# Clone
git clone https://github.com/ColumbinaNk/screenshot-api.git
cd screenshot-api

# Start
docker compose up -d

# Screenshot!
curl -o screenshot.png "http://localhost:8000/v1/screenshot?url=https://example.com"

# API docs
open http://localhost:8000/docs
```

> ⚠️ **Security Notice:** By default, no API key is set (anyone can use your API). Set `API_KEY` in `.env` before exposing to public internet.

## API

### `POST /v1/screenshot`

```json
{
  "url": "https://example.com",
  "width": 1280,
  "height": 720,
  "full_page": false,
  "format": "png",
  "quality": 80,
  "wait_ms": 0,
  "wait_selector": null
}
```

### `GET /v1/screenshot?url=...`

| Param | Default | Description |
|-------|---------|-------------|
| `url` | required | Target URL |
| `width` | 1280 | Viewport width (320-3840) |
| `height` | 720 | Viewport height (320-2160) |
| `full_page` | false | Capture full scrollable page |
| `format` | png | `png` or `jpeg` |
| `quality` | 80 | JPEG quality (1-100) |
| `wait_ms` | 0 | Wait before capture (ms) |
| `wait_selector` | null | Wait for CSS selector |

### `GET /health`

Returns browser status and uptime.

## Configuration

All via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 8000 | Server port |
| `API_KEY` | (empty) | API key (empty = no auth) |
| `RATE_LIMIT` | 60 | Requests per minute per IP |
| `CACHE_ENABLED` | true | Enable screenshot caching |
| `CACHE_TTL` | 3600 | Cache TTL in seconds |
| `BROWSER_TIMEOUT` | 30 | Navigation timeout in seconds |
| `DEFAULT_WIDTH` | 1280 | Default viewport width |
| `DEFAULT_HEIGHT` | 720 | Default viewport height |

## With Authentication

```bash
# Set API key
echo "API_KEY=my-secret-key" > .env
docker compose up -d

# Use it
curl -H "X-API-Key: my-secret-key" "http://localhost:8000/v1/screenshot?url=https://example.com"
```

## Tech Stack

- **Python** + **FastAPI** — async web framework
- **Camoufox** — anti-detection Firefox browser
- **Xvfb** — virtual display for headed mode
- **SQLite** — rate limit persistence
- **Docker** — containerized deployment

## License

MIT
