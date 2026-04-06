from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.redis import init_redis, close_redis
from app.routers import auth, users, projects, milestones, comments, collaborations, wall, feed


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    # Startup
    await init_redis()
    yield
    # Shutdown
    await close_redis()


def create_app() -> FastAPI:
    app = FastAPI(
        title="DevPulse API",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    prefix = "/api/v1"

    app.include_router(auth.router,             prefix=f"{prefix}/auth")
    app.include_router(users.router,            prefix=f"{prefix}/users")
    app.include_router(projects.router,         prefix=f"{prefix}/projects")
    app.include_router(milestones.router,       prefix=f"{prefix}/projects")
    app.include_router(comments.router,         prefix=f"{prefix}/projects")
    app.include_router(collaborations.router,   prefix=f"{prefix}/projects")
    app.include_router(wall.router,             prefix=f"{prefix}/wall")
    app.include_router(feed.router,             prefix=f"{prefix}/feed")

    @app.get("/health", tags=["health"])
    async def health_check() -> dict:
        return {"status": "ok", "version": "1.0.0"}

    return app


app = create_app()