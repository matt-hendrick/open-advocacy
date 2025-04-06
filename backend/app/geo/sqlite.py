from typing import List, Dict, Any
from uuid import UUID
import json
from shapely.geometry import Point, shape
from sqlalchemy import select, update

from app.geo.base import GeoProvider
from app.models.orm.models import Jurisdiction


class SQLiteGeoProvider(GeoProvider):
    """SQLite implementation of geographic operations using Shapely"""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def point_in_jurisdictions(self, lat: float, lon: float) -> List[UUID]:
        """
        Find all jurisdiction IDs that contain the given point using Shapely
        """
        # Create point
        point = Point(lon, lat)
        matching_ids = []

        async with self.session_factory() as session:
            # Get all jurisdictions with boundaries
            query = select(Jurisdiction).where(Jurisdiction.boundary.is_not(None))
            result = await session.execute(query)
            jurisdictions = result.scalars().all()

            # Check each jurisdiction
            for jurisdiction in jurisdictions:
                try:
                    # Parse boundary
                    if not jurisdiction.boundary:
                        continue

                    boundary_data = jurisdiction.boundary
                    if isinstance(boundary_data, str):
                        boundary_data = json.loads(boundary_data)

                    # Extract geometry from GeoJSON
                    if boundary_data.get("type") == "FeatureCollection":
                        # Handle feature collections
                        for feature in boundary_data.get("features", []):
                            if feature.get("geometry"):
                                geom = shape(feature["geometry"])
                                if geom.contains(point):
                                    matching_ids.append(jurisdiction.id)
                                    break
                    elif boundary_data.get("type") == "Feature":
                        # Handle single feature
                        if boundary_data.get("geometry"):
                            geom = shape(boundary_data["geometry"])
                            if geom.contains(point):
                                matching_ids.append(jurisdiction.id)
                    else:
                        # Handle direct geometry
                        geom = shape(boundary_data)
                        if geom.contains(point):
                            matching_ids.append(jurisdiction.id)

                except Exception as e:
                    print(f"Error checking jurisdiction {jurisdiction.id}: {e}")
                    continue

        return matching_ids

    async def store_jurisdiction_boundary(
        self, jurisdiction_id: UUID, geojson: Dict[str, Any]
    ) -> bool:
        """
        Store a boundary for a jurisdiction
        """
        async with self.session_factory() as session:
            # Update the boundary
            stmt = (
                update(Jurisdiction)
                .where(Jurisdiction.id == jurisdiction_id)
                .values(boundary=json.dumps(geojson))
            )

            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0
