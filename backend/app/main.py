from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import projects, groups, entities, status, jurisdictions, auth
from app.api.routes.admin import users, imports

import logging
import time

from app.core.config import settings
from app.db.session import create_tables, init_postgis


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger("open-advocacy")

app = FastAPI(
    title="Open Advocacy API",
    description="API for connecting citizens with representatives and tracking advocacy projects",
    version="0.1.0",
    redirect_slashes=False,  # This has been added as some deployment environments enforce this (so this helps detecting problems in dev)
)

# Add CORS middleware for development
origins = [
    "http://localhost:3000",
    "http://localhost:5173",  # Default Vite dev server port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # Get client IP and request details
    client_host = request.client.host if request.client else "unknown"

    logger.info(
        f"Request started: {request.method} {request.url.path} from {client_host}"
    )

    try:
        response = await call_next(request)

        # Calculate request processing time
        process_time = time.time() - start_time
        logger.info(
            f"Request completed: {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.3f}s"
        )

        return response
    except Exception as e:
        logger.error(
            f"Request failed: {request.method} {request.url.path} - Error: {str(e)}"
        )
        raise


@app.get("/")
async def root():
    return {"message": "Welcome to Open Advocacy API"}


app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(groups.router, prefix="/api/groups", tags=["groups"])
app.include_router(entities.router, prefix="/api/entities", tags=["entities"])
app.include_router(status.router, prefix="/api/status", tags=["status"])
app.include_router(
    jurisdictions.router, prefix="/api/jurisdictions", tags=["jurisdictions"]
)
app.include_router(
    users.router,
    prefix="/api/users",
    tags=["users"],
)
app.include_router(
    imports.router,
    prefix="/api/imports",
    tags=["imports"],
)
app.include_router(auth.router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """Initialize database and load sample data on startup."""
    logger.info(
        f"Starting application with {settings.DATABASE_PROVIDER} database provider"
    )
    try:
        await init_postgis()

        await create_tables()
    except Exception:
        logger.exception("Error initializing postgis or creating initial tables.")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
