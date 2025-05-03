#!/usr/bin/env python3
"""
Import Illinois Districts GeoJSON Script

This script:
1. Creates jurisdictions for IL House and IL Senate if they don't exist
2. Imports geojson data for IL House and IL Senate districts

Usage:
    python import_illinois_geojson.py [--create-tables] [--drop]
                                         [--house-geojson=PATH] [--senate-geojson=PATH]
"""

import asyncio
import argparse
import logging
import os
import sys
import json
from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("il_districts_import.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("il-districts-import")

try:
    from app.core.config import settings
    from app.models.orm.models import Base, Jurisdiction, District
    from app.geo.provider_factory import get_geo_provider

    logger.info("Successfully imported application modules")
except ImportError as e:
    logger.error(f"Failed to import required modules: {str(e)}")
    sys.exit(1)

# Database setup
DATABASE_URL = settings.DATABASE_URL
logger.info(f"Using database URL: {DATABASE_URL}")

# Define UUIDs for jurisdictions
IL_HOUSE_ID = UUID("e47ac10b-58cc-4372-a567-0e02b2c3d480")
IL_SENATE_ID = UUID("f47ac10b-58cc-4372-a567-0e02b2c3d481")


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


async def create_il_legislature_jurisdictions(session: AsyncSession):
    """Create Illinois House and Senate jurisdictions if they don't exist."""
    logger.info("Creating Illinois legislature jurisdictions...")

    try:
        # Check if IL House jurisdiction exists
        house_jurisdiction = await session.get(Jurisdiction, IL_HOUSE_ID)
        if not house_jurisdiction:
            # Create IL House jurisdiction
            house_jurisdiction = Jurisdiction(
                id=IL_HOUSE_ID,
                name="Illinois House of Representatives",
                description="Lower chamber of the Illinois General Assembly consisting of 118 representatives",
                level="state_house",
                created_at=datetime.now(timezone.utc),
            )
            session.add(house_jurisdiction)
            logger.info(f"Created IL House jurisdiction with ID: {IL_HOUSE_ID}")
        else:
            logger.info(f"IL House jurisdiction already exists with ID: {IL_HOUSE_ID}")

        # Check if IL Senate jurisdiction exists
        senate_jurisdiction = await session.get(Jurisdiction, IL_SENATE_ID)
        if not senate_jurisdiction:
            # Create IL Senate jurisdiction
            senate_jurisdiction = Jurisdiction(
                id=IL_SENATE_ID,
                name="Illinois State Senate",
                description="Upper chamber of the Illinois General Assembly consisting of 59 senators",
                level="state_senate",
                created_at=datetime.now(timezone.utc),
            )
            session.add(senate_jurisdiction)
            logger.info(f"Created IL Senate jurisdiction with ID: {IL_SENATE_ID}")
        else:
            logger.info(
                f"IL Senate jurisdiction already exists with ID: {IL_SENATE_ID}"
            )

        await session.commit()
        return IL_HOUSE_ID, IL_SENATE_ID
    except SQLAlchemyError as e:
        logger.error(f"Error creating IL legislature jurisdictions: {str(e)}")
        await session.rollback()
        raise


async def import_geojson_districts(
    session: AsyncSession,
    house_geojson_path: str,
    senate_geojson_path: str,
    house_jurisdiction_id: UUID,
    senate_jurisdiction_id: UUID,
) -> bool:
    """
    Import IL House and Senate districts from GeoJSON files.

    Args:
        session: Database session
        house_geojson_path: Path to IL House districts GeoJSON
        senate_geojson_path: Path to IL Senate districts GeoJSON
        house_jurisdiction_id: IL House jurisdiction ID
        senate_jurisdiction_id: IL Senate jurisdiction ID
    """
    logger.info("Importing Illinois district boundaries from GeoJSON...")

    # Get geo provider
    geo_provider = get_geo_provider()

    # Process House districts
    if house_geojson_path and os.path.exists(house_geojson_path):
        try:
            with open(house_geojson_path, "r") as f:
                house_geojson = json.load(f)

            if (
                not isinstance(house_geojson, dict)
                or house_geojson.get("type") != "FeatureCollection"
            ):
                logger.error("Invalid House GeoJSON: Expected a FeatureCollection")
            else:
                features = house_geojson.get("features", [])
                logger.info(f"Found {len(features)} House district features")

                for feature in features:
                    # Extract district number from properties - using "Name" field based on provided GeoJSON
                    district_num = feature.get("properties", {}).get("Name")
                    if not district_num:
                        logger.warning("Skipping House feature without district number")
                        continue

                    district_name = f"IL House District {district_num}"

                    # Check if district already exists
                    existing_districts = await session.execute(
                        select(District).where(
                            District.name == district_name,
                            District.jurisdiction_id == house_jurisdiction_id,
                        )
                    )
                    existing_district = existing_districts.scalar_one_or_none()

                    if existing_district:
                        logger.info(
                            f"House District {district_num} already exists, updating boundary"
                        )
                        district_id = existing_district.id
                        # Update boundary
                        await geo_provider.store_district_boundary(district_id, feature)
                    else:
                        logger.info(f"Creating new district: {district_name}")
                        # Create new district
                        new_district = District(
                            id=uuid4(),
                            name=district_name,
                            code=str(district_num),
                            jurisdiction_id=house_jurisdiction_id,
                        )

                        session.add(new_district)
                        await session.flush()  # To get the new ID

                        # Store boundary
                        await geo_provider.store_district_boundary(
                            new_district.id, feature
                        )

                logger.info(f"Processed {len(features)} House districts")
        except Exception as e:
            logger.error(f"Error processing House districts: {str(e)}")
    else:
        logger.warning(f"House GeoJSON file not found: {house_geojson_path}")

    # Process Senate districts
    if senate_geojson_path and os.path.exists(senate_geojson_path):
        try:
            with open(senate_geojson_path, "r") as f:
                senate_geojson = json.load(f)

            if (
                not isinstance(senate_geojson, dict)
                or senate_geojson.get("type") != "FeatureCollection"
            ):
                logger.error("Invalid Senate GeoJSON: Expected a FeatureCollection")
            else:
                features = senate_geojson.get("features", [])
                logger.info(f"Found {len(features)} Senate district features")

                for feature in features:
                    # Extract district number from properties - using "Name" field based on provided GeoJSON
                    district_num = feature.get("properties", {}).get("Name")
                    if not district_num:
                        logger.warning(
                            "Skipping Senate feature without district number"
                        )
                        continue

                    district_name = f"IL Senate District {district_num}"

                    # Check if district already exists
                    existing_districts = await session.execute(
                        select(District).where(
                            District.name == district_name,
                            District.jurisdiction_id == senate_jurisdiction_id,
                        )
                    )
                    existing_district = existing_districts.scalar_one_or_none()

                    if existing_district:
                        logger.info(
                            f"Senate District {district_num} already exists, updating boundary"
                        )
                        district_id = existing_district.id
                        # Update boundary
                        await geo_provider.store_district_boundary(district_id, feature)
                    else:
                        logger.info(f"Creating new district: {district_name}")
                        # Create new district
                        new_district = District(
                            id=uuid4(),
                            name=district_name,
                            code=str(district_num),
                            jurisdiction_id=senate_jurisdiction_id,
                        )

                        session.add(new_district)
                        await session.flush()  # To get the new ID

                        # Store boundary
                        await geo_provider.store_district_boundary(
                            new_district.id, feature
                        )

                logger.info(f"Processed {len(features)} Senate districts")
        except Exception as e:
            logger.error(f"Error processing Senate districts: {str(e)}")
    else:
        logger.warning(f"Senate GeoJSON file not found: {senate_geojson_path}")

    await session.commit()
    return True


async def setup_il_district_data(
    house_geojson_path: str = None,
    senate_geojson_path: str = None,
    create_tables: bool = False,
    drop_existing: bool = False,
):
    """
    Main function to set up Illinois district data.

    Args:
        house_geojson_path: Path to IL House districts GeoJSON
        senate_geojson_path: Path to IL Senate districts GeoJSON
        create_tables: Whether to create database tables
        drop_existing: Whether to drop existing tables
    """
    try:
        # Initialize database
        engine, async_session = await init_db(
            create_tables=create_tables, drop_existing=drop_existing
        )

        async with async_session() as session:
            # Create IL legislature jurisdictions
            (
                house_jurisdiction_id,
                senate_jurisdiction_id,
            ) = await create_il_legislature_jurisdictions(session)

            # Import district boundaries from GeoJSON
            if house_geojson_path or senate_geojson_path:
                await import_geojson_districts(
                    session,
                    house_geojson_path,
                    senate_geojson_path,
                    house_jurisdiction_id,
                    senate_jurisdiction_id,
                )
            else:
                logger.warning("No GeoJSON files provided, only jurisdictions created")

        # Clean up
        await engine.dispose()

        logger.info("Illinois district data import completed successfully!")

    except Exception as e:
        logger.error(f"Illinois district data import failed: {str(e)}")
        raise


async def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(
        description="Import Illinois district geojson data"
    )

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
        "--house-geojson",
        type=str,
        help="Path to GeoJSON file with IL House district boundaries",
        default="data/il_2020_state_lower_2021-09-24.json",
    )

    parser.add_argument(
        "--senate-geojson",
        type=str,
        help="Path to GeoJSON file with IL Senate district boundaries",
        default="data/il_2020_state_upper_2021-09-24.json",
    )

    args = parser.parse_args()

    await setup_il_district_data(
        house_geojson_path=args.house_geojson,
        senate_geojson_path=args.senate_geojson,
        create_tables=args.create_tables,
        drop_existing=args.drop,
    )


if __name__ == "__main__":
    asyncio.run(main())
