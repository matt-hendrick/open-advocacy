from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import projects, groups, entities, status, jurisdictions, auth
from app.api.routes.admin import users, imports

import logging
import time
import os

from app.core.config import settings

from scripts.init_db import init_db
from scripts.import_data import import_data
from scripts.import_example_project_data import import_projects
from app.services.service_factory import (
    get_cached_user_service,
    get_cached_group_service,
)
from app.models.pydantic.models import UserCreate, UserRole, GroupBase


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

if settings.ALLOWED_ORIGIN:
    origins = settings.ALLOWED_ORIGIN
else:
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

DB_INIT_LOCK_FILE = "/tmp/open_advocacy_db_initialized"


async def check_super_admin_exists() -> bool:
    """Check if a super admin user already exists in the system."""
    try:
        user_service = get_cached_user_service()
        admin_user = await user_service.get_user_by_email("matt@example.com")
        if admin_user and admin_user.role == UserRole.SUPER_ADMIN:
            return True

        return False
    except Exception as e:
        logger.error(f"Error checking for super admin: {e}")
        return False


async def create_initial_super_admin():
    """Create the initial super admin user and admin group."""
    try:
        # Get services
        group_service = get_cached_group_service()
        user_service = get_cached_user_service()

        # Create or get admin group
        groups = await group_service.list_groups()
        admin_group = None

        for group in groups:
            if group.name == "Strong Towns Chicago":
                admin_group = group
                logger.info(
                    f"Found existing admin group: {admin_group.name} ({admin_group.id})"
                )
                break

        if not admin_group:
            admin_group = await group_service.create_group(
                GroupBase(
                    name="Strong Towns Chicago",
                    description="Empowers neighborhoods to incrementally build a more financially resilient city from the bottom up, through abundant housing, safe streets, and effective transportation.",
                )
            )
            logger.info(
                f"Created new admin group: {admin_group.name} ({admin_group.id})"
            )

        admin_email = os.getenv("INITIAL_ADMIN_EMAIL", "matt@example.com")
        admin_password = os.getenv("INITIAL_ADMIN_PASSWORD", "GreenBanana56Cow!")
        admin_name = os.getenv("INITIAL_ADMIN_NAME", "System Administrator")

        # Check if user already exists
        existing_user = await user_service.get_user_by_email(admin_email)
        if existing_user:
            logger.info(f"Super admin user already exists: {admin_email}")
            return

        # Create the user data
        user_data = UserCreate(
            email=admin_email,
            password=admin_password,
            name=admin_name,
            role=UserRole.SUPER_ADMIN,
            is_active=True,
            group_id=admin_group.id,
        )

        # Create user
        user = await user_service.create_user(user_data)
        logger.info(f"Created super admin user: {user.email} (ID: {user.id})")

    except Exception as e:
        logger.error(f"Failed to create initial super admin: {str(e)}")
        raise


@app.on_event("startup")
async def startup_event():
    """Initialize database and load data on startup, ensuring it happens only once."""
    logger.info(
        f"Starting application with {settings.DATABASE_PROVIDER} database provider"
    )

    # Check if super admin already exists - if so, skip initialization
    try:
        admin_exists = await check_super_admin_exists()
        if admin_exists:
            logger.info("Super admin user exists, skipping database initialization")
            return
    except Exception as e:
        logger.error(
            f"Error checking for super admin, proceeding with initialization: {e}"
        )

    # Check file-based lock as a backup (for distributed environments)
    if os.path.exists(DB_INIT_LOCK_FILE):
        logger.info("Database initialization lock file exists, skipping initialization")
        return

    try:
        # Create lock file early to prevent race conditions
        try:
            with open(DB_INIT_LOCK_FILE, "w") as f:
                f.write(
                    f"Database initialization started at {time.strftime('%Y-%m-%d %H:%M:%S')}"
                )
        except Exception as e:
            logger.error(f"Failed to write lock file: {e}")

        logger.info("Initializing database and creating initial admin user...")

        # Step 1: Initialize database with tables, dropping existing ones
        logger.info("Creating database tables...")
        await init_db(create_tables=True, drop_existing=True)

        # Step 2: Create initial super admin user
        logger.info("Creating initial super admin user...")
        await create_initial_super_admin()

        # Step 3: Import Chicago data
        logger.info("Importing Chicago data...")
        chicago_result = await import_data("chicago")
        if chicago_result.get("steps_failed", 0) > 0:
            logger.warning("Some Chicago import steps failed")

        # Step 4: Import Illinois data
        logger.info("Importing Illinois data...")
        illinois_result = await import_data("illinois")
        if illinois_result.get("steps_failed", 0) > 0:
            logger.warning("Some Illinois import steps failed")

        # Step 5: Import projects
        logger.info("Importing projects...")
        await import_projects()

        logger.info("Database initialization completed successfully")

    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
