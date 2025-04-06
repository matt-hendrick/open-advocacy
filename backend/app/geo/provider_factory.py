from app.geo.base import GeoProvider
from app.geo.postgres import PostgresGeoProvider
from app.geo.sqlite import SQLiteGeoProvider
from app.core.config import settings
from app.db.session import get_session_factory


def get_geo_provider() -> GeoProvider:
    """Factory to create the appropriate geographic provider"""

    session_factory = get_session_factory()

    db_type = settings.DATABASE_PROVIDER.lower()

    if db_type == "postgres":
        return PostgresGeoProvider(session_factory=session_factory)
    else:
        return SQLiteGeoProvider(session_factory=session_factory)
