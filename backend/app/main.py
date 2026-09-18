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

app = create_app()

if __name__ == "__main__":
    settings = get_settings()
    config = uvicorn.Config(
        app,
        host=settings.app.HOST,
        port=settings.app.PORT,
        log_level="info",
    )
    server = uvicorn.Server(config)
    if sys.platform == "win32":
        asyncio.run(
            server.serve(),
            loop_factory=lambda: asyncio.SelectorEventLoop(selectors.SelectSelector()),
        )
    else:
        server.run()
