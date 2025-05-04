#!/usr/bin/env python3
"""
Import Illinois Legislators Script

This script:
1. Fetches IL representatives data from OpenStates API
2. Creates entity records for IL legislators
3. Optionally generates random status records for projects

Usage:
    python illinois_state_legislators_setup.py [--random-statuses] [--project-ids UUID1 UUID2...]
"""

import asyncio
import argparse
import logging
import sys
import random
import aiohttp
from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import List, Dict, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("il_legislators_import.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("il-legislators-import")

try:
    from app.core.config import settings
    from app.models.orm.models import (
        Entity,
        Jurisdiction,
        EntityStatusRecord,
        District,
        Project,
    )

    logger.info("Successfully imported application modules")
except ImportError as e:
    logger.error(f"Failed to import required modules: {str(e)}")
    sys.exit(1)

# Database setup
DATABASE_URL = settings.DATABASE_URL
logger.info(f"Using database URL: {DATABASE_URL}")


OPENSTATES_API_KEY = settings.OPENSTATES_API_KEY
if not OPENSTATES_API_KEY:
    raise ValueError("OPENSTATES_API_KEY environment variable not set")

# OpenStates API endpoint
OPENSTATES_API_BASE = "https://v3.openstates.org"
OPENSTATES_PEOPLE_ENDPOINT = f"{OPENSTATES_API_BASE}/people"

# Define UUIDs for jurisdictions (must match the ones in import_il_districts_geojson.py)
IL_HOUSE_ID = UUID("e47ac10b-58cc-4372-a567-0e02b2c3d480")
IL_SENATE_ID = UUID("f47ac10b-58cc-4372-a567-0e02b2c3d481")


async def init_db():
    """Initialize database and return engine and session factory."""
    try:
        # Create engine
        engine = create_async_engine(DATABASE_URL, echo=False)
        logger.info("Database engine created")

        # Create session factory
        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        logger.info("Session factory created")

        return engine, async_session
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise


async def verify_jurisdictions(session: AsyncSession):
    """Verify that Illinois House and Senate jurisdictions exist."""
    logger.info("Verifying Illinois legislature jurisdictions...")

    try:
        # Check if IL House jurisdiction exists
        house_jurisdiction = await session.get(Jurisdiction, IL_HOUSE_ID)
        if not house_jurisdiction:
            logger.error(f"IL House jurisdiction with ID {IL_HOUSE_ID} not found")
            logger.error(
                "Run import_il_districts_geojson.py first to create jurisdictions"
            )
            return None, None

        # Check if IL Senate jurisdiction exists
        senate_jurisdiction = await session.get(Jurisdiction, IL_SENATE_ID)
        if not senate_jurisdiction:
            logger.error(f"IL Senate jurisdiction with ID {IL_SENATE_ID} not found")
            logger.error(
                "Run import_il_districts_geojson.py first to create jurisdictions"
            )
            return None, None

        logger.info("Successfully verified Illinois legislature jurisdictions")
        return IL_HOUSE_ID, IL_SENATE_ID
    except SQLAlchemyError as e:
        logger.error(f"Error verifying IL legislature jurisdictions: {str(e)}")
        raise


async def fetch_il_legislators() -> Dict[str, List[Dict[str, Any]]]:
    """
    Fetch Illinois legislators data from OpenStates API.

    Returns:
        Dictionary with 'house' and 'senate' lists of legislator data
    """
    logger.info("Fetching Illinois legislators from OpenStates API...")

    headers = {
        "X-API-Key": OPENSTATES_API_KEY,
    }

    legislators = {"house": [], "senate": []}

    try:
        async with aiohttp.ClientSession() as session:
            # Fetch IL legislators
            # We'll need to paginate to get all results
            url = f"{OPENSTATES_PEOPLE_ENDPOINT}"

            params = {
                "jurisdiction": "ocd-jurisdiction/country:us/state:il/government",
                "include": [
                    "other_names",
                    "other_identifiers",
                    "links",
                    "sources",
                    "offices",
                ],
                "per_page": 50,
            }

            page = 1
            total_fetched = 0

            while True:
                params["page"] = page
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(
                            f"API request failed: {response.status} - {error_text}"
                        )
                        break

                    data = await response.json()
                    results = data.get("results", [])

                    if not results:
                        break

                    # Sort legislators into house and senate
                    for legislator in results:
                        current_role = legislator.get("current_role", {})
                        if current_role.get("org_classification") == "lower":
                            legislators["house"].append(legislator)
                        elif current_role.get("org_classification") == "upper":
                            legislators["senate"].append(legislator)

                    total_fetched += len(results)
                    logger.info(f"Fetched {len(results)} legislators (page {page})")

                    # Check pagination
                    pagination = data.get("pagination", {})
                    if page >= pagination.get("max_page", 1):
                        break

                    page += 1

            logger.info(
                f"Fetched {len(legislators['house'])} House representatives and {len(legislators['senate'])} Senators"
            )
            logger.info(f"Total fetched: {total_fetched}")
            return legislators
    except Exception as e:
        logger.error(f"Error fetching legislators: {str(e)}")
        return legislators


async def fetch_legislators_by_location(
    session: AsyncSession, latitude: float, longitude: float
) -> List[Dict[str, Any]]:
    """
    Fetch legislators for a specific location using OpenStates API.

    Args:
        session: Database session
        latitude: Latitude coordinate
        longitude: Longitude coordinate

    Returns:
        List of legislator data
    """
    logger.info(f"Fetching legislators for location: {latitude}, {longitude}")

    headers = {
        "X-API-Key": OPENSTATES_API_KEY,
    }

    legislators = []

    try:
        async with aiohttp.ClientSession() as session:
            # Use the people.geo endpoint
            url = f"{OPENSTATES_API_BASE}/people.geo"

            params = {
                "lat": latitude,
                "lng": longitude,
                "include": [
                    "other_names",
                    "other_identifiers",
                    "links",
                    "sources",
                    "offices",
                ],
            }

            async with session.get(url, headers=headers, params=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(
                        f"API request failed: {response.status} - {error_text}"
                    )
                    return []

                data = await response.json()
                legislators = data.get("results", [])

                logger.info(f"Fetched {len(legislators)} legislators for location")
                return legislators
    except Exception as e:
        logger.error(f"Error fetching legislators by location: {str(e)}")
        return []


async def create_legislator_entities(
    session: AsyncSession,
    legislators: Dict[str, List[Dict[str, Any]]],
    house_jurisdiction_id: UUID,
    senate_jurisdiction_id: UUID,
) -> List[Entity]:
    """
    Create entity records for Illinois legislators.

    Args:
        session: Database session
        legislators: Dictionary with house and senate legislator data
        house_jurisdiction_id: IL House jurisdiction ID
        senate_jurisdiction_id: IL Senate jurisdiction ID

    Returns:
        List of created entity objects
    """
    logger.info("Creating entity records for Illinois legislators...")

    entities = []

    try:
        # Process House representatives
        for rep in legislators["house"]:
            # Get district info
            district_num = rep.get("current_role", {}).get("district")
            if not district_num:
                logger.warning(f"Skipping rep without district: {rep.get('name')}")
                continue

            district_name = f"IL House District {district_num}"

            # Find matching district
            district_result = await session.execute(
                select(District).where(
                    District.name == district_name,
                    District.jurisdiction_id == house_jurisdiction_id,
                )
            )
            district = district_result.scalar_one_or_none()

            if not district:
                logger.warning(
                    f"District not found for {district_name}, creating basic district"
                )
                district = District(
                    id=uuid4(),
                    name=district_name,
                    code=str(district_num),
                    jurisdiction_id=house_jurisdiction_id,
                )
                session.add(district)
                await session.flush()

            # Extract contact info
            email = rep.get("email")
            website = None
            phone = None
            address = None

            # Extract from offices
            for office in rep.get("offices", []):
                if not phone and office.get("voice"):
                    phone = office.get("voice")
                if not address and office.get("address"):
                    address = office.get("address")

            # Extract from links
            for link in rep.get("links", []):
                if link.get("note") == "homepage" or not website:
                    website = link.get("url")

            # Check if entity already exists
            existing_result = await session.execute(
                select(Entity).where(
                    Entity.name == rep.get("name"),
                    Entity.jurisdiction_id == house_jurisdiction_id,
                )
            )
            existing_entity = existing_result.scalar_one_or_none()

            if existing_entity:
                logger.info(
                    f"Entity already exists for Rep {rep.get('name')}, updating"
                )
                existing_entity.title = "State Representative"
                existing_entity.email = email
                existing_entity.phone = phone
                existing_entity.website = website
                existing_entity.address = address
                entities.append(existing_entity)
            else:
                # Create entity
                entity = Entity(
                    id=uuid4(),
                    name=rep.get("name"),
                    title="State Representative",
                    entity_type="state_representative",
                    jurisdiction_id=house_jurisdiction_id,
                    district_id=district.id,
                    email=email,
                    phone=phone,
                    website=website,
                    address=address,
                )

                session.add(entity)
                entities.append(entity)

        # Process Senators
        for senator in legislators["senate"]:
            # Get district info
            district_num = senator.get("current_role", {}).get("district")
            if not district_num:
                logger.warning(
                    f"Skipping senator without district: {senator.get('name')}"
                )
                continue

            district_name = f"IL Senate District {district_num}"

            # Find matching district
            district_result = await session.execute(
                select(District).where(
                    District.name == district_name,
                    District.jurisdiction_id == senate_jurisdiction_id,
                )
            )
            district = district_result.scalar_one_or_none()

            if not district:
                logger.warning(
                    f"District not found for {district_name}, creating basic district"
                )
                district = District(
                    id=uuid4(),
                    name=district_name,
                    code=str(district_num),
                    jurisdiction_id=senate_jurisdiction_id,
                )
                session.add(district)
                await session.flush()

            # Extract contact info
            email = senator.get("email")
            website = None
            phone = None
            address = None

            # Extract from offices
            for office in senator.get("offices", []):
                if not phone and office.get("voice"):
                    phone = office.get("voice")
                if not address and office.get("address"):
                    address = office.get("address")

            # Extract from links
            for link in senator.get("links", []):
                if link.get("note") == "homepage" or not website:
                    website = link.get("url")

            # Check if entity already exists
            existing_result = await session.execute(
                select(Entity).where(
                    Entity.name == senator.get("name"),
                    Entity.jurisdiction_id == senate_jurisdiction_id,
                )
            )
            existing_entity = existing_result.scalar_one_or_none()

            if existing_entity:
                logger.info(
                    f"Entity already exists for Senator {senator.get('name')}, updating"
                )
                existing_entity.title = "State Senator"
                existing_entity.email = email
                existing_entity.phone = phone
                existing_entity.website = website
                existing_entity.address = address
                entities.append(existing_entity)
            else:
                # Create entity
                entity = Entity(
                    id=uuid4(),
                    name=senator.get("name"),
                    title="State Senator",
                    entity_type="state_senator",
                    jurisdiction_id=senate_jurisdiction_id,
                    district_id=district.id,
                    email=email,
                    phone=phone,
                    website=website,
                    address=address,
                )

                session.add(entity)
                entities.append(entity)

        await session.commit()
        logger.info(f"Created or updated {len(entities)} legislator entities")

        return entities
    except SQLAlchemyError as e:
        logger.error(f"Error creating legislator entities: {str(e)}")
        await session.rollback()
        raise


async def create_random_status_records(
    session: AsyncSession, entities: List[Entity], project_ids: List[UUID]
) -> List[EntityStatusRecord]:
    """Create random status records for legislators on specified projects."""

    if not project_ids:
        logger.info("No projects specified for status records, skipping")
        return []

    logger.info(
        f"Creating random status records for {len(entities)} legislators on {len(project_ids)} projects..."
    )

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
            for project_id in project_ids:
                # Verify project exists
                project = await session.get(Project, project_id)
                if not project:
                    logger.warning(f"Project with ID {project_id} not found, skipping")
                    continue

                # Check if status record already exists
                existing_result = await session.execute(
                    select(EntityStatusRecord).where(
                        EntityStatusRecord.entity_id == entity.id,
                        EntityStatusRecord.project_id == project_id,
                    )
                )
                existing_record = existing_result.scalar_one_or_none()

                if existing_record:
                    logger.info(
                        f"Status record already exists for {entity.name} on project {project.title}, updating"
                    )
                    existing_record.status = random.choice(status_options)
                    existing_record.updated_at = datetime.now(timezone.utc)
                    status_records.append(existing_record)
                else:
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
                        id=uuid4(),
                        entity_id=entity.id,
                        project_id=project_id,
                        status=status,
                        notes=notes,
                        updated_at=datetime.now(timezone.utc),
                        updated_by="admin",
                    )

                    status_records.append(record)
                    session.add(record)

        await session.commit()
        logger.info(f"Created or updated {len(status_records)} random status records")

        return status_records
    except SQLAlchemyError as e:
        logger.error(f"Error creating random status records: {str(e)}")
        await session.rollback()
        raise


async def import_il_legislators_data(
    generate_random_statuses: bool = False,
    project_ids: List[UUID] = None,
    use_geo_endpoint: bool = False,
    latitude: float = None,
    longitude: float = None,
):
    """
    Main function to import Illinois legislators data.

    Args:
        generate_random_statuses: Whether to generate random status records
        project_ids: List of project IDs to generate status records for
        use_geo_endpoint: Whether to use the geo endpoint instead of fetching all legislators
        latitude: Latitude for geo endpoint (if use_geo_endpoint is True)
        longitude: Longitude for geo endpoint (if use_geo_endpoint is True)
    """
    try:
        # Initialize database
        engine, async_session = await init_db()

        async with async_session() as session:
            # Verify jurisdictions exist
            house_jurisdiction_id, senate_jurisdiction_id = await verify_jurisdictions(
                session
            )

            if not house_jurisdiction_id or not senate_jurisdiction_id:
                logger.error(
                    "Jurisdictions not found. Run import_il_districts_geojson.py first."
                )
                return

            # Fetch legislator data
            legislators = {"house": [], "senate": []}

            if use_geo_endpoint and latitude is not None and longitude is not None:
                # Use geo endpoint to fetch legislators for location
                geo_legislators = await fetch_legislators_by_location(
                    session, latitude, longitude
                )

                # Sort legislators into house and senate
                for legislator in geo_legislators:
                    current_role = legislator.get("current_role", {})
                    if current_role.get("org_classification") == "lower":
                        legislators["house"].append(legislator)
                    elif current_role.get("org_classification") == "upper":
                        legislators["senate"].append(legislator)
            else:
                # Fetch all IL legislators
                legislators = await fetch_il_legislators()

            if not legislators["house"] and not legislators["senate"]:
                logger.error("No legislators found from OpenStates API")
                return

            # Create entity records for legislators
            entities = await create_legislator_entities(
                session, legislators, house_jurisdiction_id, senate_jurisdiction_id
            )

            # Optionally create random status records
            if generate_random_statuses and project_ids:
                await create_random_status_records(session, entities, project_ids)

        # Clean up
        await engine.dispose()

        logger.info("Illinois legislators import completed successfully!")

    except Exception as e:
        logger.error(f"Illinois legislators import failed: {str(e)}")
        raise


async def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(description="Import Illinois legislators data")

    parser.add_argument(
        "--random-statuses",
        action="store_true",
        help="Assign random statuses for legislators on specified projects",
    )

    parser.add_argument(
        "--project-ids",
        type=str,
        nargs="+",
        help="UUIDs of projects to generate status records for (space-separated)",
    )

    parser.add_argument(
        "--use-geo",
        action="store_true",
        help="Use geo endpoint to fetch legislators for a specific location",
    )

    parser.add_argument(
        "--latitude",
        type=float,
        help="Latitude for geo endpoint (if --use-geo is specified)",
    )

    parser.add_argument(
        "--longitude",
        type=float,
        help="Longitude for geo endpoint (if --use-geo is specified)",
    )

    args = parser.parse_args()

    # Convert project IDs to UUIDs
    project_ids = []
    if args.project_ids:
        for pid in args.project_ids:
            try:
                project_ids.append(UUID(pid))
            except ValueError:
                logger.error(f"Invalid project ID: {pid}")

    # Validate geo parameters
    use_geo = args.use_geo
    if use_geo and (args.latitude is None or args.longitude is None):
        logger.error(
            "Both latitude and longitude must be provided when using --use-geo"
        )
        sys.exit(1)

    await import_il_legislators_data(
        generate_random_statuses=args.random_statuses,
        project_ids=project_ids,
        use_geo_endpoint=use_geo,
        latitude=args.latitude,
        longitude=args.longitude,
    )


if __name__ == "__main__":
    asyncio.run(main())
