"""
GrowFlow — Backend Application Entrypoint.

Thin ASGI application module per Phase 6A/6C frozen architecture.
Use `python -m backend.app.main` to start the development server.
"""

from __future__ import annotations

import asyncio
import selectors
import sys
import uvicorn

from backend.app.config.settings import get_settings
from backend.app.factory import create_app

# Ensure compatible asyncio event loop policy for psycopg on Windows.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = create_app()

if __name__ == "__main__":
    settings = get_settings()
    config = uvicorn.Config(
        "backend.app.main:app",
        host=settings.app.HOST,
        port=settings.app.PORT,
        log_level="info",
        loop="asyncio:SelectorEventLoop" if sys.platform == "win32" else "auto",
    )
    server = uvicorn.Server(config)
    server.run()
