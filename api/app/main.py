from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .cache import Cache, make_cache
from .config import Settings, get_settings
from .db import Database
from .observability import configure_logging, request_context
from .routes import router


def create_app(settings: Settings | None = None, cache: Cache | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(title="Portfolio Tracker API", version="1.0.0")
    app.state.settings = settings
    app.state.db = Database(settings.database_url)
    app.state.cache = cache or make_cache(settings.redis_url)

    if settings.cors_origin_list:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origin_list,
            allow_methods=["GET", "POST", "PUT", "DELETE"],
            allow_headers=["Content-Type", "X-API-Key", "X-Request-ID"],
        )
    app.middleware("http")(request_context)
    app.include_router(router)
    return app
