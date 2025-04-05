import asyncio
import argparse
import logging
import os
import sys
import uuid
import aiohttp
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("chicago_import.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("chicago-import")

try:
    from app.models.orm.models import (
        Base,
        Project,
        Group,
        Entity,
        Jurisdiction,
    )

    logger.info("Successfully imported ORM models")
except ImportError as e:
    logger.error(f"Failed to import ORM models: {str(e)}")
    sys.exit(1)

# Database setup
DATABASE_URL = settings.DATABASE_URL
logger.info(f"Using database URL: {DATABASE_URL}")

# Chicago API endpoint
CHICAGO_ALDERMEN_API = "https://data.cityofchicago.org/resource/c6ie-9e6c.json"

# Define UUIDs
CHICAGO_ID = UUID("f47ac10b-58cc-4372-a567-0e02b2c3d479")
CHICAGO_COUNCIL_ID = UUID("a7b8c9d0-e1f2-3a4b-5c6d-7e8f9a0b1c2d")
PARTICIPATORY_BUDGET_PROJECT_ID = UUID("d4e5f6a7-8b9c-7d8e-2f3a-5b6c7d8e9f0a")
BUDGET_ADVOCATES_GROUP_ID = UUID("4b5c6d7e-8f9a-0b1c-2d3e-4f5a6b7c8d9e")


async def init_db(create_tables: bool = False, drop_existing: bool = False) -> tuple:
    """Initialize database and return engine and session factory."""
    try:
        # Create data directory if it doesn't exist
        os.makedirs("./data", exist_ok=True)

        # Create engine
        engine = create_async_engine(DATABASE_URL, echo=False)
        logger.info("Database engine created")

        # Create database tables if requested
        if create_tables:
            async with engine.begin() as conn:
                if drop_existing:
                    await conn.run_sync(Base.metadata.drop_all)
                    logger.info("Dropped all existing tables")

                await conn.run_sync(Base.metadata.create_all)
                logger.info("Created all necessary tables")

        # Create session factory
        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        logger.info("Session factory created")

        return engine, async_session
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise


async def fetch_chicago_aldermen():
    """Fetch Chicago aldermen data from the API."""
    logger.info(f"Fetching Chicago aldermen data from: {CHICAGO_ALDERMEN_API}")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(CHICAGO_ALDERMEN_API) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Successfully fetched data for {len(data)} aldermen")
                    return data
                else:
                    logger.error(f"Failed to fetch data: {response.status}")
                    return None
    except Exception as e:
        logger.error(f"Error fetching aldermen data: {str(e)}")
        return None


async def create_chicago_council_jurisdiction(session: AsyncSession) -> UUID:
    """Create Chicago City Council jurisdiction."""
    logger.info("Creating Chicago City Council jurisdiction...")

    try:
        # Create Chicago City Council jurisdiction
        chicago_council = Jurisdiction(
            id=CHICAGO_COUNCIL_ID,
            name="Chicago City Council",
            description="Legislative branch of the City of Chicago government consisting of 50 alderpersons",
            level="city_council",
            parent_jurisdiction_id=CHICAGO_ID,  # Parent is the Chicago jurisdiction
            created_at=datetime.now(timezone.utc),
        )

        session.add(chicago_council)
        await session.commit()
        logger.info(
            f"Created Chicago City Council jurisdiction with ID: {CHICAGO_COUNCIL_ID}"
        )

        return CHICAGO_COUNCIL_ID
    except SQLAlchemyError as e:
        logger.error(f"Error creating Chicago City Council jurisdiction: {str(e)}")
        await session.rollback()
        raise


async def create_budget_advocates_group(session: AsyncSession) -> UUID:
    """Create a group for budget advocacy."""
    logger.info("Creating Budget Advocates group...")

    try:
        group = Group(
            id=BUDGET_ADVOCATES_GROUP_ID,
            name="Chicago Budget Advocates",
            description="Coalition of community organizations advocating for participatory budgeting and fiscal transparency",
            created_at=datetime.now(timezone.utc),
        )

        session.add(group)
        await session.commit()
        logger.info(
            f"Created Budget Advocates group with ID: {BUDGET_ADVOCATES_GROUP_ID}"
        )

        return BUDGET_ADVOCATES_GROUP_ID
    except SQLAlchemyError as e:
        logger.error(f"Error creating Budget Advocates group: {str(e)}")
        await session.rollback()
        raise


async def create_aldermen_entities(
    session: AsyncSession, aldermen_data, jurisdiction_id: UUID
):
    """Create entity records for Chicago aldermen."""
    logger.info("Creating Chicago aldermen entities...")

    try:
        entities = []

        for alderman in aldermen_data:
            # Extract name
            name = alderman.get("alderman", "")

            # Extract ward number
            ward = alderman.get("ward", "")
            district = f"Ward {ward}"

            # Extract contact info
            email = alderman.get("email", "")
            ward_phone = alderman.get("ward_phone", "")
            city_hall_phone = alderman.get("city_hall_phone", "")

            # Choose the ward phone as primary, but if missing use city hall phone
            phone = ward_phone if ward_phone else city_hall_phone

            # Extract addresses
            ward_address = alderman.get("address", "")
            zipcode = alderman.get("zipcode", "")
            city_hall_address = alderman.get("city_hall_address", "")
            city_hall_zipcode = alderman.get("city_hall_zipcode", "")

            # Create full address
            if ward_address:
                full_address = f"{ward_address}, Chicago, IL {zipcode}"
            else:
                full_address = f"{city_hall_address}, Chicago, IL {city_hall_zipcode}"

            # Extract website if available
            website = None
            if "website" in alderman and isinstance(alderman["website"], dict):
                website = alderman["website"].get("url", None)

            # Create entity
            entity = Entity(
                id=uuid.uuid4(),
                name=name,
                title="Alderperson",
                entity_type="alderman",
                jurisdiction_id=jurisdiction_id,
                location_module_id="chicago",
                email=email,
                phone=phone,
                website=website,
                address=full_address,
                district=district,
            )

            entities.append(entity)

        # Add all entities to database
        session.add_all(entities)
        await session.commit()
        logger.info(f"Created {len(entities)} aldermen entities")

        return entities
    except SQLAlchemyError as e:
        logger.error(f"Error creating aldermen entities: {str(e)}")
        await session.rollback()
        raise


async def create_participatory_budget_project(
    session: AsyncSession, jurisdiction_id: UUID, group_id: UUID
):
    """Create a project for Chicago participatory budgeting."""
    logger.info("Creating Chicago Participatory Budgeting project...")

    try:
        project = Project(
            id=PARTICIPATORY_BUDGET_PROJECT_ID,
            title="Chicago Participatory Budgeting Initiative",
            description="Advocating for expanded participatory budgeting across all 50 wards to increase civic engagement and equitable resource allocation.",
            status="active",
            active=True,
            link="https://example.com/chicago-pb-initiative",
            preferred_status="solid_approval",
            template_response="I am writing to express my strong support for expanding participatory budgeting across all 50 Chicago wards. Participatory budgeting has proven successful in the wards where it has been implemented, giving residents direct control over how tax dollars are spent in their communities. This democratic process increases transparency, civic engagement, and ensures public funds address the most pressing community needs. I urge you to support this initiative and help make Chicago a leader in democratic governance.",
            created_by="admin",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            jurisdiction_id=jurisdiction_id,
            group_id=group_id,
        )

        session.add(project)
        await session.commit()
        logger.info(
            f"Created Participatory Budgeting project with ID: {PARTICIPATORY_BUDGET_PROJECT_ID}"
        )

        return project
    except SQLAlchemyError as e:
        logger.error(f"Error creating Participatory Budgeting project: {str(e)}")
        await session.rollback()
        raise


async def main():
    """Main function to run the script."""
    logger.info("Starting Chicago City Council data import...")

    parser = argparse.ArgumentParser(description="Import Chicago City Council data")
    parser.add_argument(
        "--create-tables",
        action="store_true",
        help="Create database tables if they don't exist",
    )
    parser.add_argument(
        "--drop",
        action="store_true",
        help="Drop existing tables before creating new ones (only used with --create-tables)",
    )
    args = parser.parse_args()

    try:
        # Initialize database
        engine, async_session = await init_db(
            create_tables=args.create_tables, drop_existing=args.drop
        )

        # Fetch Chicago aldermen data
        aldermen_data = await fetch_chicago_aldermen()

        if not aldermen_data:
            logger.error("Failed to fetch aldermen data. Exiting.")
            return

        logger.info(f"Successfully fetched {len(aldermen_data)} aldermen records")

        # Create session for database operations
        async with async_session() as session:
            # Create Chicago City Council jurisdiction
            council_jurisdiction_id = await create_chicago_council_jurisdiction(session)

            # Create advocacy group
            group_id = await create_budget_advocates_group(session)

            # Create aldermen entities
            await create_aldermen_entities(
                session, aldermen_data, council_jurisdiction_id
            )

            # Create project for Chicago City Council
            await create_participatory_budget_project(
                session, council_jurisdiction_id, group_id
            )

        # Clean up
        await engine.dispose()

        logger.info("Chicago City Council data import completed successfully!")

    except Exception as e:
        logger.error(f"Chicago data import failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
