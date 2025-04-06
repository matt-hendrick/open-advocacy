from typing import List, Dict, Any
from uuid import UUID
from sqlalchemy import text

from app.geo.base import GeoProvider
from app.db.session import get_session


class PostgresGeoProvider(GeoProvider):
    """PostgreSQL implementation of geographic operations using PostGIS"""

    def __init__(self, session_factory=get_session):
        self.session_factory = session_factory

    async def point_in_jurisdictions(self, lat: float, lon: float) -> List[UUID]:
        """
        Find all jurisdiction IDs that contain the given point using PostGIS
        """
        async with self.session_factory() as session:
            # Create point in WGS84 coordinate system
            # TODO: Clean this up
            query = text("""
                SELECT j.id 
                FROM jurisdictions j
                WHERE ST_Contains(
                    ST_SetSRID(ST_GeomFromGeoJSON(j.boundary->>'geometry'), 4326),
                    ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)
                )
            """)

            result = await session.execute(query, {"lon": lon, "lat": lat})
            return [row[0] for row in result]

    async def store_jurisdiction_boundary(
        self, jurisdiction_id: UUID, geojson: Dict[str, Any]
    ) -> bool:
        """
        Store a boundary for a jurisdiction, optimizing for PostGIS
        """
        async with self.session_factory() as session:
            # Update the boundary
            query = text("""
                UPDATE jurisdictions
                SET boundary = :geojson
                WHERE id = :jurisdiction_id
            """)

            result = await session.execute(
                query, {"geojson": geojson, "jurisdiction_id": str(jurisdiction_id)}
            )

            await session.commit()
            return result.rowcount > 0
