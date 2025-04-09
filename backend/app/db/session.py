from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import text
import logging


from app.core.config import settings
from app.models.orm.models import Base

logger = logging.getLogger("session.py")

# Dictionary to store engines for different database types
_engines = {}
_session_factories = {}


def get_engine():
    """Get the SQLAlchemy engine for the configured database."""
    db_type = settings.DATABASE_PROVIDER.lower()

    if db_type not in _engines:
        # Configure engine based on database type
        if db_type == "sqlite":
            # SQLite-specific configurations
            _engines[db_type] = create_async_engine(
                settings.DATABASE_URL,
                echo=settings.DB_ECHO,
                # SQLite doesn't support pool_pre_ping
                # Using NullPool to avoid thread issues with SQLite
                poolclass=NullPool,
            )
        elif db_type == "postgres":
            # PostgreSQL-specific configurations
            _engines[db_type] = create_async_engine(
                settings.DATABASE_URL,
                echo=settings.DB_ECHO,
                pool_size=settings.DB_POOL_SIZE,
                max_overflow=settings.DB_MAX_OVERFLOW,
                pool_pre_ping=True,
                pool_recycle=settings.DB_POOL_RECYCLE,
            )
        else:
            raise ValueError(f"Unsupported database provider: {db_type}")

    return _engines[db_type]


def get_session_factory():
    """Get the async session factory for the current database."""
    db_type = settings.DATABASE_PROVIDER.lower()

    if db_type not in _session_factories:
        engine = get_engine()
        _session_factories[db_type] = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

    return _session_factories[db_type]


async def get_session():
    """Get a database session for dependency injection."""
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


# TODO: Reconsider this
async def create_tables():
    """Create all tables in the database if they don't exist."""
    engine = get_engine()
    async with engine.begin() as conn:
        # Create tables without dropping existing ones
        await conn.run_sync(Base.metadata.create_all)


async def init_postgis():
    """Initialize PostGIS extension if using PostgreSQL."""
    if settings.DATABASE_PROVIDER.lower() == "postgres":
        engine = get_engine()
        async with engine.begin() as conn:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
            logger.info("PostGIS extension initialized")
