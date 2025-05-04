from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import projects, groups, entities, status, jurisdictions
import logging
import time
import os

from app.core.config import settings

from scripts.init_db import init_db
from scripts.import_data import import_data
from scripts.import_example_project_data import import_projects


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
    root_path="/",
    redirect_slashes=False,  # This has been added as some deployment environments enforce this (so this helps detecting problems in dev)
)

# Add CORS middleware for development
origins = [
    "http://localhost:3000",
    "http://localhost:5173",  # Default Vite dev server port
]

if settings.ALLOWED_ORIGIN:
    origins = settings.ALLOWED_ORIGIN

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


# TODO: Remove this
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

DB_INIT_LOCK_FILE = "/tmp/open_advocacy_db_initialized"


# TODO: Consider if this is necessary
@app.on_event("startup")
async def startup_event():
    """Initialize database and load data on startup, ensuring it happens only once."""
    logger.info(
        f"Starting application with {settings.DATABASE_PROVIDER} database provider"
    )

    # Check if we need to initialize the database
    should_init_db = True

    # For distributed environments (multiple workers), use a file-based lock
    if os.path.exists(DB_INIT_LOCK_FILE):
        logger.info("Database initialization lock file exists, skipping initialization")
        should_init_db = False

    if should_init_db:
        try:
            try:
                with open(DB_INIT_LOCK_FILE, "w") as f:
                    f.write(
                        f"Database initialized at {time.strftime('%Y-%m-%d %H:%M:%S')}"
                    )
            except Exception as e:
                logger.error(f"Failed to write lock file... {e}")
            logger.info("Initializing database...")

            # Step 1: Initialize database with tables, dropping existing ones
            logger.info("Creating database tables...")
            await init_db(create_tables=True, drop_existing=True)

            # Step 2: Import Chicago data
            logger.info("Importing Chicago data...")
            chicago_result = await import_data("chicago")
            if chicago_result.get("steps_failed", 0) > 0:
                logger.warning("Some Chicago import steps failed")

            # Step 3: Import Illinois data
            logger.info("Importing Illinois data...")
            illinois_result = await import_data("illinois")
            if illinois_result.get("steps_failed", 0) > 0:
                logger.warning("Some Illinois import steps failed")

            # Step 4: Import projects
            logger.info("Importing projects...")
            await import_projects()

            logger.info("Database initialization completed successfully")

        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
