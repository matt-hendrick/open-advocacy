from typing import Any
import os
from pathlib import Path

from app.imports.locations.base import LocationConfig
from app.imports.sources.chicago_alderpersons import ChicagoAlderpersonDataSource
from app.imports.sources.geojson import GeoJSONDataSource
from app.imports.importers.jurisdiction_importer import JurisdictionImporter
from app.imports.importers.district_importer import DistrictImporter
from app.imports.importers.entity_importer import EntityImporter
from app.services.service_factory import (
    get_cached_jurisdiction_service,
    get_cached_district_service,
    get_cached_entity_service,
)
from app.core.config import settings


class ChicagoLocationConfig(LocationConfig):
    """Configuration for Chicago data imports."""

    def __init__(self, geojson_path: str | None = None):
        """
        Initialize Chicago location config.

        Args:
            geojson_path: Path to Chicago wards GeoJSON file (optional)
        """
        base_dir = Path(settings.DATA_DIR or "data")
        self.geojson_path = geojson_path or os.path.join(
            base_dir, "chicago-wards.geojson"
        )

    @property
    def name(self) -> str:
        return "Chicago"

    @property
    def description(self) -> str:
        return "City of Chicago with City Council and Wards"

    @property
    def import_steps(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "Import Chicago City Council jurisdiction",
                "importer": "jurisdiction_importer",
                "config": {
                    "name": "Chicago City Council",
                    "description": "Legislative branch of the City of Chicago government consisting of 50 alderpersons",
                    "level": "city_council",
                },
            },
            {
                "name": "Import Chicago Wards GeoJSON",
                "importer": "district_importer",
                "data_source": "wards_geojson",
                "config": {
                    "jurisdiction_name": "Chicago City Council",
                    "district_name_property": "ward",
                    "district_name_prefix": "Ward ",
                },
            },
            {
                "name": "Import Chicago Alderpersons",
                "importer": "entity_importer",
                "data_source": "alderperson_data",
                "config": {
                    "jurisdiction_name": "Chicago City Council",
                    "entity_type": "alderperson",
                    "title": "Alderperson",
                    "mapping": {
                        "name": "alderman",
                        "district_code": "ward",
                        "email": "email",
                        "phone": ["ward_phone", "city_hall_phone"],
                        "website": "website.url",
                        "address": ["address", "zipcode"],
                    },
                },
            },
        ]

    async def get_importers(self) -> dict[str, Any]:
        """Get configured importers for Chicago."""
        jurisdiction_service = get_cached_jurisdiction_service()
        district_service = get_cached_district_service()
        entity_service = get_cached_entity_service()

        return {
            "importers": {
                "jurisdiction_importer": JurisdictionImporter(jurisdiction_service),
                "district_importer": DistrictImporter(
                    district_service, jurisdiction_service
                ),
                "entity_importer": EntityImporter(
                    entity_service, district_service, jurisdiction_service
                ),
            },
            "data_sources": {
                "alderperson_data": ChicagoAlderpersonDataSource(),
                "wards_geojson": GeoJSONDataSource(file_path=self.geojson_path),
            },
        }
