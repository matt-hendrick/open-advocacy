import asyncio
import logging
from app.services.service_factory import (
    get_cached_jurisdiction_service,
    get_cached_entity_service,
    get_cached_project_service,
    get_cached_group_service,
    get_cached_status_service,
)
from app.models.pydantic.models import ProjectBase, EntityStatusRecord, EntityStatus

OPT_IN_WARDS = [
    1, 4, 6, 12, 14, 22, 25, 26, 27, 29, 30, 32, 33, 35, 40, 43, 44, 46, 47, 49
]

PROJECT_TITLE = "ADU Opt-In"
PROJECT_DESCRIPTION = (
    "Tracking Chicago alderpersons who have opted in to support Accessory Dwelling Units (ADUs). "
    "Alders who opted in are marked as strongly agree; others are marked as neutral."
)
PROJECT_LINK = None 

async def import_adu_project_data():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("adu-opt-in-import")

    jurisdiction_service = get_cached_jurisdiction_service()
    entity_service = get_cached_entity_service()
    project_service = get_cached_project_service()
    group_service = get_cached_group_service()
    status_service = get_cached_status_service()

    jurisdiction = await jurisdiction_service.find_by_name("Chicago City Council")
    if not jurisdiction:
        logger.error("Chicago City Council jurisdiction not found.")
        return

    group = await group_service.find_or_create_by_name(
        "Strong Towns Chicago",
        "Empowers neighborhoods to incrementally build a more financially resilient city.",
    )

    # Create the ADU Opt-In project
    project = await project_service.create_project(
        ProjectBase(
            title=PROJECT_TITLE,
            description=PROJECT_DESCRIPTION,
            status="active",
            active=True,
            link=PROJECT_LINK,
            preferred_status=EntityStatus.SOLID_APPROVAL,
            jurisdiction_id=jurisdiction.id,
            group_id=group.id,
            created_by="admin",
        )
    )
    logger.info(f"Created project: {project.title}")

    # Get all alderperson entities for Chicago
    entities = await entity_service.list_entities(jurisdiction_id=jurisdiction.id)
    logger.info(f"Found {len(entities)} alderpersons.")

    # Set status for each alderperson
    for entity in entities:
        # Try to get ward number from district code or name
        ward_number = None
        if hasattr(entity, "district_name") and entity.district_name:
            # Expecting format "Ward 1", "Ward 4", etc.
            if entity.district_name.lower().startswith("ward "):
                try:
                    ward_number = int(entity.district_name.split(" ")[1])
                except Exception:
                    pass
        elif hasattr(entity, "district_code") and entity.district_code:
            try:
                ward_number = int(entity.district_code)
            except Exception:
                pass

        is_opt_in = ward_number in OPT_IN_WARDS if ward_number is not None else False
        status = EntityStatus.SOLID_APPROVAL if is_opt_in else EntityStatus.NEUTRAL

        status_record = EntityStatusRecord(
            entity_id=entity.id,
            project_id=project.id,
            status=status,
            notes=f"Ward {ward_number} opted in to allow ADUs to be built in the ward" if is_opt_in else "No opt-in record",
            updated_by="admin",
        )
        await status_service.create_status_record(status_record)
        logger.info(f"Set status for {entity.name} (Ward {ward_number}): {status}")

    logger.info("ADU Opt-In project import completed.")

if __name__ == "__main__":
    asyncio.run(import_adu_project_data())