from typing import Any, Type
import logging

from app.imports.locations.base import LocationConfig

logger = logging.getLogger("import-orchestrator")


class ImportOrchestrator:
    """Orchestrates data imports based on location configurations."""

    def __init__(self):
        self.available_locations = {}

    def register_location(
        self, location_key: str, location_config: Type[LocationConfig]
    ):
        """Register a location configuration."""
        self.available_locations[location_key] = location_config

    async def import_location(self, location_key: str, **kwargs) -> dict[str, Any]:
        """
        Import data for a specific location.
        """
        if location_key not in self.available_locations:
            raise ValueError(f"Unknown location: {location_key}")

        # Create location config
        location_config = self.available_locations[location_key]()

        # Get importers and data sources
        importers_config = await location_config.get_importers()
        importers = importers_config.get("importers", {})
        data_sources = importers_config.get("data_sources", {})

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
            import_config = step.get(
                "config", {}
            ).copy()  # Make a copy to avoid modifying the original

            # Handle special case for district_importer with geojson data
            if (
                importer_key == "district_importer"
                and data
                and isinstance(data, dict)
                and data.get("type") == "FeatureCollection"
            ):
                import_config["geojson_data"] = data
            elif data:
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
        }

    async def get_available_locations(self) -> list[dict[str, Any]]:
        """Get information about available locations."""
        locations = []
        for key, config_class in self.available_locations.items():
            config = config_class()
            locations.append(
                {
                    "key": key,
                    "name": config.name,
                    "description": config.description,
                    "steps": len(config.import_steps),
                }
            )
        return locations
