from typing import List, Dict, Any
from uuid import UUID
import json
from shapely.geometry import Point, shape
from sqlalchemy import select

from app.geo.base import GeoProvider
from app.models.orm.models import District


class SQLiteGeoProvider(GeoProvider):
    """SQLite implementation using Shapely"""

    async def districts_containing_point(self, lat: float, lon: float) -> List[UUID]:
        """Find districts containing a point using Shapely"""
        point = Point(lon, lat)
        matching_ids = []

        async with self.session_factory() as session:
            # Get all districts with boundaries
            query = select(District).where(District.boundary.is_not(None))
            result = await session.execute(query)
            districts = result.scalars().all()

            # Check each district
            for district in districts:
                try:
                    boundary_data = district.boundary
                    if isinstance(boundary_data, str):
                        boundary_data = json.loads(boundary_data)

                    # Extract geometry
                    if boundary_data.get("type") == "FeatureCollection":
                        for feature in boundary_data.get("features", []):
                            if feature.get("geometry"):
                                geom = shape(feature["geometry"])
                                if geom.contains(point):
                                    matching_ids.append(district.id)
                                    break
                    elif boundary_data.get("type") == "Feature":
                        if boundary_data.get("geometry"):
                            geom = shape(boundary_data["geometry"])
                            if geom.contains(point):
                                matching_ids.append(district.id)
                    else:
                        geom = shape(boundary_data)
                        if geom.contains(point):
                            matching_ids.append(district.id)
                except Exception as e:
                    print(f"Error checking district {district.id}: {e}")

        return matching_ids

    async def store_district_boundary(
        self, district_id: UUID, geojson: Dict[str, Any]
    ) -> bool:
        """Store a boundary for a district"""
        async with self.session_factory() as session:
            # Get district
            district = await session.get(District, district_id)
            if not district:
                return False

            # Update boundary
            district.boundary = (
                json.dumps(geojson) if not isinstance(geojson, str) else geojson
            )
            await session.commit()
            return True
