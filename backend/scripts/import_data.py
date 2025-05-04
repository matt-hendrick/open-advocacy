# scripts/test_import.py
import asyncio
import argparse
import logging
import sys
from typing import Any

from app.imports.orchestrator import ImportOrchestrator
from app.imports.locations.chicago import ChicagoLocationConfig
from app.imports.locations.illinois import IllinoisLocationConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("import_test.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("import-test")


class TestImportOrchestrator(ImportOrchestrator):
    """Extended Import Orchestrator with dry run capabilities."""

    async def import_location(
        self, location_key: str, dry_run: bool = False, **kwargs
    ) -> dict[str, Any]:
        """
        Import data for a specific location with dry run option.

        Args:
            location_key: Key for the location configuration
            dry_run: If True, doesn't make actual database changes
            **kwargs: Additional parameters for the import

        Returns:
            Dict with import results
        """
        if location_key not in self.available_locations:
            raise ValueError(f"Unknown location: {location_key}")

        # Create location config
        location_config = self.available_locations[location_key]()

        # Get importers and data sources
        importers_config = await location_config.get_importers()
        importers = importers_config.get("importers", {})
        data_sources = importers_config.get("data_sources", {})

        # Apply dry run transformation to importers if needed
        if dry_run:
            logger.info("Running in DRY RUN mode - no database changes will be made")
            for importer_key, importer in importers.items():
                original_import = importer.import_data

                async def make_dry_run_import(original_fn, importer_type):
                    async def dry_run_import(**import_kwargs):
                        logger.info(
                            f"DRY RUN: Would import with {importer_type} using params:"
                        )
                        for key, value in import_kwargs.items():
                            if key in ["data", "geojson_data"]:
                                data_len = None
                                try:
                                    if isinstance(value, list):
                                        data_len = len(value)
                                    elif (
                                        isinstance(value, dict) and "features" in value
                                    ):
                                        data_len = len(value.get("features", []))
                                except:
                                    pass

                                if data_len:
                                    logger.info(f"  {key}: <{data_len} items>")
                                else:
                                    logger.info(f"  {key}: <data object>")
                            else:
                                logger.info(f"  {key}: {value}")

                        # Return mock results based on the importer type
                        if "jurisdiction" in importer_type:
                            from uuid import uuid4
                            from types import SimpleNamespace

                            mock_jurisdiction = SimpleNamespace(
                                id=uuid4(),
                                name=import_kwargs.get("name", "Mock Jurisdiction"),
                                level=import_kwargs.get("level", "mock"),
                            )
                            return {
                                "operation": "dry_run",
                                "jurisdiction": mock_jurisdiction,
                            }
                        elif "district" in importer_type:
                            return {
                                "districts_created": 5,
                                "districts_updated": 2,
                                "districts_error": 0,
                                "districts_total": 7,
                                "dry_run": True,
                                "districts": [],
                            }
                        elif "entity" in importer_type:
                            return {
                                "entities_created": 10,
                                "entities_updated": 3,
                                "entities_error": 0,
                                "entities_total": 13,
                                "dry_run": True,
                                "entities": [],
                            }
                        return {"dry_run": True}

                    return dry_run_import

                # Replace the original import method with our dry run version
                importer.import_data = await make_dry_run_import(
                    original_import, importer_key
                )

        # Execute import steps
        results = []
        for step in location_config.import_steps:
            step_name = step.get("name", "Unnamed step")

            # Check if this step should be skipped
            step_skip_key = f"{step_name}.skip"
            if step_skip_key in kwargs and kwargs[step_skip_key]:
                logger.info(f"Skipping step: {step_name}")
                continue

            logger.info(f"Starting import step: {step_name}")

            # Get importer
            importer_key = step.get("importer")
            if not importer_key or importer_key not in importers:
                logger.error(f"Invalid importer specified for step: {step_name}")
                results.append(
                    {
                        "step": step_name,
                        "status": "error",
                        "message": f"Invalid importer: {importer_key}",
                    }
                )
                continue

            importer = importers[importer_key]

            # Get data source if specified
            data_source_key = step.get("data_source")
            data = None
            if data_source_key:
                if data_source_key not in data_sources:
                    logger.error(f"Invalid data source specified for step: {step_name}")
                    results.append(
                        {
                            "step": step_name,
                            "status": "error",
                            "message": f"Invalid data source: {data_source_key}",
                        }
                    )
                    continue

                data_source = data_sources[data_source_key]
                try:
                    data = await data_source.fetch_data()
                except Exception as e:
                    logger.error(f"Error fetching data for step {step_name}: {str(e)}")
                    results.append(
                        {
                            "step": step_name,
                            "status": "error",
                            "message": f"Data fetch error: {str(e)}",
                        }
                    )
                    continue

            # Prepare config for import
            import_config = step.get("config", {}).copy()
            if (
                "geojson_data" in import_config
                and import_config["geojson_data"] is True
            ):
                # Pass the GeoJSON data from the data source to the importer
                import_config["geojson_data"] = data
                # Remove the flag
                del import_config["geojson_data"]
            elif data is not None:
                # Regular data handling
                import_config["data"] = data

            # Merge with any override parameters from kwargs
            for key, value in kwargs.items():
                if key.startswith(f"{step_name}."):
                    param_key = key.split(".", 1)[1]
                    if param_key != "skip":  # Skip the skip flag
                        import_config[param_key] = value

            # Validate and execute import
            try:
                if await importer.validate_import(**import_config):
                    import_result = await importer.import_data(**import_config)
                    results.append(
                        {
                            "step": step_name,
                            "status": "success",
                            "result": import_result,
                        }
                    )
                else:
                    logger.error(f"Validation failed for step: {step_name}")
                    results.append(
                        {
                            "step": step_name,
                            "status": "error",
                            "message": "Validation failed",
                        }
                    )
            except Exception as e:
                logger.error(f"Error executing import step {step_name}: {str(e)}")
                results.append(
                    {
                        "step": step_name,
                        "status": "error",
                        "message": f"Import error: {str(e)}",
                    }
                )

        return {
            "location": location_key,
            "steps_total": len(location_config.import_steps),
            "steps_succeeded": len([r for r in results if r["status"] == "success"]),
            "steps_failed": len([r for r in results if r["status"] == "error"]),
            "results": results,
            "dry_run": dry_run,
        }


async def test_import(
    location_key: str, steps_to_run: list[str] = None, dry_run: bool = False
):
    """Test importing data for a specific location."""
    logger.info(f"Testing import for location: {location_key}")
    logger.info(f"Dry run mode: {dry_run}")

    # Set up orchestrator
    orchestrator = TestImportOrchestrator()
    orchestrator.register_location("chicago", ChicagoLocationConfig)
    orchestrator.register_location("illinois", IllinoisLocationConfig)

    if location_key not in orchestrator.available_locations:
        logger.error(f"Unknown location: {location_key}")
        return

    # Get information about available steps
    location_config = orchestrator.available_locations[location_key]()
    all_steps = [step["name"] for step in location_config.import_steps]
    logger.info(f"Available import steps: {all_steps}")

    # Prepare override parameters if specific steps are requested
    override_params = {}
    if steps_to_run:
        # Set up to only run specified steps
        for step in all_steps:
            if step not in steps_to_run:
                override_params[f"{step}.skip"] = True

    # Run import
    try:
        result = await orchestrator.import_location(
            location_key, dry_run=dry_run, **override_params
        )

        # Print results
        logger.info(f"Import completed for {location_key}")
        if dry_run:
            logger.info("DRY RUN - No database changes were made")
        logger.info(f"Steps total: {result['steps_total']}")
        logger.info(f"Steps succeeded: {result['steps_succeeded']}")
        logger.info(f"Steps failed: {result['steps_failed']}")

        if result["steps_failed"] > 0:
            logger.warning("Some import steps failed:")
            for step_result in result["results"]:
                if step_result["status"] == "error":
                    logger.warning(
                        f"  - {step_result['step']}: {step_result.get('message', 'Unknown error')}"
                    )

        # Print detailed results
        logger.info("Detailed results:")
        for step_result in result["results"]:
            if step_result["status"] == "success":
                step_name = step_result["step"]
                step_data = step_result.get("result", {})
                logger.info(f"Step: {step_name}")

                # Print summary stats based on importer type
                if (
                    "jurisdictions" in step_name.lower()
                    or "jurisdiction" in step_name.lower()
                ):
                    operation = step_data.get("operation", "unknown")
                    logger.info(f"  Operation: {operation}")
                    if "jurisdiction" in step_data:
                        logger.info(f"  ID: {step_data['jurisdiction'].id}")
                        logger.info(f"  Name: {step_data['jurisdiction'].name}")

                elif "district" in step_name.lower():
                    created = step_data.get("districts_created", 0)
                    updated = step_data.get("districts_updated", 0)
                    total = step_data.get("districts_total", 0)
                    logger.info(f"  Districts created: {created}")
                    logger.info(f"  Districts updated: {updated}")
                    logger.info(f"  Districts total: {total}")

                elif (
                    "entities" in step_name.lower()
                    or "representatives" in step_name.lower()
                    or "alderperson" in step_name.lower()
                    or "senator" in step_name.lower()
                ):
                    created = step_data.get("entities_created", 0)
                    updated = step_data.get("entities_updated", 0)
                    total = step_data.get("entities_total", 0)
                    logger.info(f"  Entities created: {created}")
                    logger.info(f"  Entities updated: {updated}")
                    logger.info(f"  Entities total: {total}")

    except Exception as e:
        logger.error(f"Import failed: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test location data imports")
    parser.add_argument(
        "location",
        choices=["chicago", "illinois"],
        help="Location to import",
    )
    parser.add_argument(
        "--steps",
        nargs="+",
        help="Specific steps to run (by name)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Test configuration without making changes to the database",
    )

    args = parser.parse_args()

    asyncio.run(test_import(args.location, args.steps, args.dry_run))
