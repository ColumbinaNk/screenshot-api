FROM debian:trixie-slim

# System deps — Xvfb + Firefox deps + Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv \
    xvfb x11-utils \
    libgtk-3-0 libdbus-glib-1-2 libxt6 libasound2t64 \
    libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 \
    libgbm1 libnss3 libatk-bridge2.0-0 libatspi2.0-0 \
    fonts-liberation fonts-noto-color-emoji \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python deps (venv for PEP 668 compliance)
COPY requirements.txt .
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# Download Camoufox browser binary
RUN python3 -c "from camoufox.installer import install; install()" || \
    camoufox fetch

# App code
COPY app/ ./app/

# Entry point
COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./docker-entrypoint.sh"]
