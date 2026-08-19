"""Set up logging before importing anything else"""

import sentry_sdk

from api.constants import (
    CORS_ALLOWED_ORIGINS,
    DEPLOYMENT_MODE,
    ENABLE_TELEMETRY,
    PUBLIC_BASE_URL,
    SENTRY_DSN,
)
from api.logging_config import ENVIRONMENT, setup_logging

# Set up logging and get the listener for cleanup
setup_logging()


if SENTRY_DSN and (
    DEPLOYMENT_MODE != "oss" or (DEPLOYMENT_MODE == "oss" and ENABLE_TELEMETRY)
):
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        send_default_pii=True,
        environment=ENVIRONMENT,
    )
    print(f"Sentry initialized in environment: {ENVIRONMENT}")


from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from api.constants import REDIS_URL
from api.errors.mps import MPS_UNAVAILABLE_PUBLIC_MESSAGE, MPSUnavailableError
from api.mcp_server import mcp
from api.routes.main import router as main_router
from api.services.pipecat.tracing_config import (
    handle_langfuse_sync,
    load_all_org_langfuse_credentials,
)
from api.services.worker_sync.manager import (
    WorkerSyncManager,
    set_worker_sync_manager,
)
from api.services.worker_sync.protocol import WorkerSyncEventType
from api.tasks.arq import get_arq_redis

API_PREFIX = "/api/v1"

mcp_app = mcp.http_app(path="/", stateless_http=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with mcp_app.lifespan(app):
        # warmup arq pool
        await get_arq_redis()

        # Pre-register all org-specific Langfuse exporters so they're ready
        # before any pipeline runs, without per-call DB lookups.
        await load_all_org_langfuse_credentials()

        # Start cross-worker sync manager so config changes propagate to all workers
        sync_manager = WorkerSyncManager(REDIS_URL)
        sync_manager.register(
            WorkerSyncEventType.LANGFUSE_CREDENTIALS, handle_langfuse_sync
        )
        await sync_manager.start()
        set_worker_sync_manager(sync_manager)

        # Event-loop lag gauge — per-pod saturation signal read off
        # /health/active-calls during autoscaling load tests.
        from api.services.observability import loop_lag

        loop_lag.start()

        yield  # Run app

        # Shutdown sequence - this runs when FastAPI is shutting down
        logger.info("Starting graceful shutdown...")
        await sync_manager.stop()
        await loop_lag.stop()


app = FastAPI(
    title="GenQuantaa Calling Agent API",
    description="API for the GenQuantaa Calling Agent Platform",
    version="1.0.0",
    openapi_url=f"{API_PREFIX}/openapi.json",
    lifespan=lifespan,
    servers=[
        {"url": "http://localhost:8000", "description": "Local development"},
    ],
)


@app.exception_handler(MPSUnavailableError)
async def handle_mps_unavailable_error(
    _request: Request,
    _exc: MPSUnavailableError,
) -> JSONResponse:
    """Tell callers this is a Dograh outage, not invalid customer config."""

    return JSONResponse(
        status_code=503,
        content={"detail": MPS_UNAVAILABLE_PUBLIC_MESSAGE},
    )


# Configure CORS.
# Allow development origins (http://localhost:3010, http://127.0.0.1:3010, etc.)
# plus any explicitly configured CORS_ALLOWED_ORIGINS with allow_credentials=True
# so browser requests sending cookies/headers succeed without CORS errors.
dev_origins = [
    "http://localhost:3010",
    "http://127.0.0.1:3010",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

cors_origins: list[str] = []
for origin in dev_origins:
    if origin not in cors_origins:
        cors_origins.append(origin)

for origin in CORS_ALLOWED_ORIGINS:
    if origin and origin != "*" and origin not in cors_origins:
        cors_origins.append(origin)

if PUBLIC_BASE_URL and PUBLIC_BASE_URL not in cors_origins:
    cors_origins.append(PUBLIC_BASE_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _add_public_embed_cors_middleware() -> None:
    from api.routes.public_embed import PublicEmbedCORSMiddleware

    app.add_middleware(PublicEmbedCORSMiddleware, api_prefix=API_PREFIX)


_add_public_embed_cors_middleware()

api_router = APIRouter()

# include subrouters here
api_router.include_router(main_router)

# main router with api prefix
app.include_router(api_router, prefix=API_PREFIX)

# Mount the MCP server — agents reach it at /api/v1/mcp over Streamable HTTP,
# authenticating with the same X-API-Key header used by the REST API.
# Mounted under /api/v1 so existing reverse-proxy rules (nginx etc.) route it
# without any extra configuration.
app.mount(f"{API_PREFIX}/mcp", mcp_app)
