"""
Application initialization module.
Handles database setup, admin user creation, and data imports.
"""

import logging
import time
import os

from scripts.init_db import init_db
from scripts.import_data import import_data
from scripts.import_example_project_data import import_projects
from app.services.service_factory import (
    get_cached_user_service,
    get_cached_group_service,
)
from app.models.pydantic.models import UserCreate, UserRole, GroupBase

logger = logging.getLogger("open-advocacy")

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


async def initialize_application():
    """
    Initialize the application: database, admin user, and data imports.
    Returns True if initialization was performed, False if skipped.
    """
    logger.info("Starting application initialization check...")

    # Check if super admin already exists - if so, skip initialization
    try:
        admin_exists = await check_super_admin_exists()
        if admin_exists:
            logger.info("Super admin user exists, skipping database initialization")
            return False
    except Exception as e:
        logger.error(
            f"Error checking for super admin, proceeding with initialization: {e}"
        )

    # Check file-based lock as a backup (for distributed environments)
    if os.path.exists(DB_INIT_LOCK_FILE):
        logger.info("Database initialization lock file exists, skipping initialization")
        return False

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
        return True

    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        # Remove lock file on failure so initialization can be retried