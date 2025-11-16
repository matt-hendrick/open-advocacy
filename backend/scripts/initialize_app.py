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


async def initialize_application():
    """
    Initialize the application: database, admin user, and data imports.
    Returns True if initialization was performed, False if skipped.
    """
    logger.info("Starting application initialization check...")

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
        return True

    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        # Remove lock file on failure so initialization can be retried