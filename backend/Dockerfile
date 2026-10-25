# ============================================================
# GrowFlow Backend — Container Runtime
# Python 3.12 Slim Linux Container
# ============================================================

FROM python:3.12-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app:$PYTHONPATH" \
    APP_HOST=0.0.0.0 \
    APP_PORT=8000 \
    PATH="/home/appuser/.local/bin:$PATH"

# Create a non-privileged system user for runtime execution
RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -m -s /bin/bash appuser

WORKDIR /app

# Install dependencies first for layer caching
COPY requirements.txt ./

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend application source and migration configuration
COPY backend ./backend
COPY alembic.ini ./

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Healthcheck testing the lightweight liveness probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/live')" || exit 1

# Default container command. Using CMD allows 'docker compose run --rm backend <cmd>'
# to cleanly override the startup process for Alembic migrations, test runs, or shell access.
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
