import asyncio
import argparse
import logging
import os
import sys
import uuid
import aiohttp
import random
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
        EntityStatusRecord,
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
STRONG_TOWNS_GROUP_ID = UUID("4b5c6d7e-8f9a-0b1c-2d3e-4f5a6b7c8d9e")

# Project UUIDs
HOUSING_PROJECT_ID = UUID("d4e5f6a7-8b9c-7d8e-2f3a-5b6c7d8e9f0a")
SAFE_STREETS_PROJECT_ID = UUID("e5f6a7b8-9c0d-8e9f-3a4b-6c7d8e9f0a1b")
PARKING_REFORM_PROJECT_ID = UUID("f6a7b8c9-0d1e-9f0a-4b5c-7d8e9f0a1b2c")


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


async def create_strong_towns_group(session: AsyncSession) -> UUID:
    """Create Strong Towns Chicago advocacy group."""
    logger.info("Creating Strong Towns Chicago group...")

    try:
        group = Group(
            id=STRONG_TOWNS_GROUP_ID,
            name="Strong Towns Chicago",
            description="Empowers neighborhoods to incrementally build a more financially resilient city from the bottom up, through abundant housing, safe streets, and effective transportation.",
            created_at=datetime.now(timezone.utc),
        )

        session.add(group)
        await session.commit()
        logger.info(
            f"Created Strong Towns Chicago group with ID: {STRONG_TOWNS_GROUP_ID}"
        )

        return STRONG_TOWNS_GROUP_ID
    except SQLAlchemyError as e:
        logger.error(f"Error creating Strong Towns Chicago group: {str(e)}")
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


async def create_strong_towns_projects(
    session: AsyncSession, jurisdiction_id: UUID, group_id: UUID
):
    """Create projects for Strong Towns Chicago initiatives."""
    logger.info("Creating Strong Towns Chicago projects...")

    try:
        # Housing Project
        housing_project = Project(
            id=HOUSING_PROJECT_ID,
            title="Accessory Dwelling Units Legalization",
            description="Advocating for legalizing accessory dwelling units (ADUs) throughout Chicago and Illinois to increase housing supply and affordability while allowing for gentle density increases in existing neighborhoods.",
            status="active",
            active=True,
            link="https://example.com/strong-towns-adus",
            preferred_status="solid_approval",
            template_response="I am writing to express my strong support for legalizing accessory dwelling units throughout Chicago and Illinois. ADUs provide affordable housing options, help homeowners with mortgage costs, allow for aging in place, and increase density without changing neighborhood character. They're a proven solution to our housing shortage that has worked well in other cities. I urge you to support ADU legalization to help build a more financially resilient Chicago with housing options for everyone.",
            created_by="admin",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            jurisdiction_id=jurisdiction_id,
            group_id=group_id,
        )

        # Safe Streets Project
        safe_streets_project = Project(
            id=SAFE_STREETS_PROJECT_ID,
            title="Complete Streets Implementation",
            description="Working to implement comprehensive safe streets policies including protected bike lanes, traffic calming measures, improved pedestrian infrastructure, and better transit access throughout Chicago.",
            status="active",
            active=True,
            link="https://example.com/strong-towns-safe-streets",
            preferred_status="solid_approval",
            template_response="I am writing to express my support for implementing complete streets policies in Chicago. Too many of our streets prioritize cars over people, leading to dangerous conditions for pedestrians and cyclists. Complete streets with protected bike lanes, traffic calming measures, and accessible transit options make our city safer for everyone, reduce pollution, and create more vibrant neighborhoods. I urge you to support these essential safety improvements for all Chicagoans.",
            created_by="admin",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            jurisdiction_id=jurisdiction_id,
            group_id=group_id,
        )

        # Parking Reform Project
        parking_reform_project = Project(
            id=PARKING_REFORM_PROJECT_ID,
            title="Parking Minimum Elimination",
            description="Advocating for the elimination of parking minimums in Chicago's zoning code to enable more affordable housing development, reduce car dependency, and create more walkable neighborhoods.",
            status="active",
            active=True,
            link="https://example.com/strong-towns-parking-reform",
            preferred_status="solid_approval",
            template_response="I am writing to express my support for eliminating parking minimums in Chicago's zoning code. Current requirements force developers to build expensive parking spaces regardless of actual demand, which increases housing costs, wastes valuable urban land, and encourages more car use and traffic congestion. By eliminating these outdated requirements, we can make housing more affordable, enable small-scale neighborhood development, and create a more walkable, sustainable city. Many successful cities have already made this change with positive results. I urge you to support this important reform.",
            created_by="admin",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            jurisdiction_id=jurisdiction_id,
            group_id=group_id,
        )

        projects = [housing_project, safe_streets_project, parking_reform_project]
        session.add_all(projects)
        await session.commit()

        logger.info(f"Created {len(projects)} Strong Towns Chicago projects")
        return projects
    except SQLAlchemyError as e:
        logger.error(f"Error creating Strong Towns Chicago projects: {str(e)}")
        await session.rollback()
        raise


async def create_random_status_records(session: AsyncSession, entities, projects):
    """Create random status records for aldermen on projects."""
    logger.info("Creating random status records for aldermen...")

    try:
        status_options = [
            "solid_approval",
            "leaning_approval",
            "neutral",
            "leaning_disapproval",
            "solid_disapproval",
        ]
        status_records = []

        for entity in entities:
            for project in projects:
                # Randomly select a status
                status = random.choice(status_options)

                # Random notes based on status
                if status == "solid_approval":
                    notes = f"Strongly supports the {project.title} initiative and has expressed willingness to advocate for it."
                elif status == "leaning_approval":
                    notes = f"Generally supportive of {project.title} but has some questions about implementation details."
                elif status == "neutral":
                    notes = f"Has not taken a clear position on {project.title} and has requested more information."
                elif status == "leaning_disapproval":
                    notes = f"Has expressed some concerns about {project.title} and its potential impacts."
                else:  # solid_disapproval
                    notes = f"Opposes the {project.title} initiative and has publicly stated concerns."

                # Create status record
                record = EntityStatusRecord(
                    id=uuid.uuid4(),
                    entity_id=entity.id,
                    project_id=project.id,
                    status=status,
                    notes=notes,
                    updated_at=datetime.now(timezone.utc),
                    updated_by="admin",
                )

                status_records.append(record)

        session.add_all(status_records)
        await session.commit()
        logger.info(f"Created {len(status_records)} random status records")

        return status_records
    except SQLAlchemyError as e:
        logger.error(f"Error creating random status records: {str(e)}")
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
    parser.add_argument(
        "--random-statuses",
        action="store_true",
        help="Assign random statuses for aldermen on each project",
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

            # Create Strong Towns Chicago group
            group_id = await create_strong_towns_group(session)

            # Create aldermen entities
            entities = await create_aldermen_entities(
                session, aldermen_data, council_jurisdiction_id
            )

            # Create projects for Strong Towns Chicago
            projects = await create_strong_towns_projects(
                session, council_jurisdiction_id, group_id
            )

            # Optionally create random status records
            if args.random_statuses:
                await create_random_status_records(session, entities, projects)

        # Clean up
        await engine.dispose()

        logger.info("Chicago City Council data import completed successfully!")

    except Exception as e:
        logger.error(f"Chicago data import failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
