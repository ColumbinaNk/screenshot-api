# Contributing

Contributions are welcome! Here's how to get started.

## Development

```bash
# Clone
git clone https://github.com/yourname/screenshot-api.git
cd screenshot-api

# Run locally (without Docker)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start Xvfb (Linux)
Xvfb :99 -screen 0 1280x1024x24 -nolisten tcp &
export DISPLAY=:99

# Run
uvicorn app.main:app --reload
```

## Code Style

- Python 3.11+
- Type hints on all functions
- Docstrings for public APIs
- Keep it simple — minimal dependencies

## Pull Requests

1. Fork the repo
2. Create a branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m 'Add my feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

## Issues

Found a bug? Open an issue with:
- Steps to reproduce
- Expected vs actual behavior
- OS, Python version, Docker version
