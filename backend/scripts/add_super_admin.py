"""
Script to create an initial super admin user.
Usage: python -m scripts.add_super_admin
"""

import asyncio
import argparse
import logging
import sys


from app.services.service_factory import (
    get_cached_user_service,
    get_cached_group_service,
)
from app.models.pydantic.models import UserCreate, UserRole, GroupBase

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("admin_create.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("admin-create")


async def create_admin_user(email: str, password: str, name: str):
    """Create a super admin user with an admin group."""
    try:
        # Get services
        group_service = get_cached_group_service()
        user_service = get_cached_user_service()

        # Create or get admin group
        groups = await group_service.list_groups()
        admin_group = None

        for group in groups:
            if group.name == "Administrators":
                admin_group = group
                logger.info(
                    f"Found existing admin group: {admin_group.name} ({admin_group.id})"
                )
                break

        if not admin_group:
            admin_group = await group_service.create_group(
                GroupBase(
                    name="Administrators",
                    description="Default administrator group with full system access",
                )
            )
            logger.info(
                f"Created new admin group: {admin_group.name} ({admin_group.id})"
            )

        # Check if user already exists
        existing_user = await user_service.get_user_by_email(email)
        if existing_user:
            logger.warning(f"User with email {email} already exists")
            return

        # Create the user data
        user_data = UserCreate(
            email=email,
            password=password,
            name=name,
            role=UserRole.SUPER_ADMIN,
            is_active=True,
            group_id=admin_group.id,
        )

        # Create user
        user = await user_service.create_user(user_data)
        logger.info(f"Created super admin user: {user.email} (ID: {user.id})")

    except Exception as e:
        logger.error(f"Failed to create admin user: {str(e)}")
        import traceback

        traceback.print_exc()


def main():
    parser = argparse.ArgumentParser(description="Create an admin user")
    parser.add_argument("--email", default="admin@example.com", help="Admin email")
    parser.add_argument(
        "--password", default="AdminPassword123!", help="Admin password"
    )
    parser.add_argument("--name", default="System Administrator", help="Admin name")

    args = parser.parse_args()

    logger.info(f"Creating admin user with email: {args.email}")
    asyncio.run(create_admin_user(args.email, args.password, args.name))
    logger.info("Admin user creation process completed")


if __name__ == "__main__":
    main()
