"""
GrowFlow — Backend Application Entrypoint.

Thin ASGI application module per Phase 6A/6C frozen architecture.
Use `uvicorn backend.app.main:app --reload` to start the development server.
"""

from __future__ import annotations

import uvicorn

from backend.app.config.settings import get_settings
from backend.app.factory import create_app

app = create_app()

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "backend.app.main:app",
        host=settings.app.HOST,
        port=settings.app.PORT,
        reload=settings.app.DEBUG,
    )
