from typing import Type, TypeVar, List, Any, Optional
from uuid import UUID
from sqlalchemy import select, func

from app.db.base import DatabaseProvider
from app.models.orm.models import Base

T = TypeVar("T")  # Pydantic model type
ModelType = TypeVar("ModelType", bound=Base)  # SQLAlchemy model type


class SQLProvider(DatabaseProvider[T, UUID]):
    """
    SQL implementation of the database provider interface.
    """

    def __init__(
        self,
        pydantic_model: Type[T],
        orm_model: Type[ModelType],
        session_factory: callable,
    ):
        self.pydantic_model = pydantic_model
        self.orm_model = orm_model
        self.session_factory = session_factory

    async def get(self, id: UUID) -> Optional[T]:
        """Get an item by ID."""
        async with self.session_factory() as session:
            db_obj = await session.get(self.orm_model, id)
            if not db_obj:
                return None
            return self._to_pydantic(db_obj)

    async def list(self, skip: int = 0, limit: int = 100) -> List[T]:
        """List all items with pagination."""
        async with self.session_factory() as session:
            query = select(self.orm_model).offset(skip).limit(limit)
            result = await session.execute(query)
            orm_models = result.scalars().all()
            return [self._to_pydantic(item) for item in orm_models]

    async def count(self) -> int:
        """Count total items."""
        async with self.session_factory() as session:
            query = select(func.count()).select_from(self.orm_model)
            result = await session.execute(query)
            return result.scalar_one()

    async def create(self, obj_in: Any) -> T:
        """Create a new item."""
        async with self.session_factory() as session:
            # Convert to dict if needed
            if isinstance(obj_in, dict):
                create_data = obj_in
            else:
                create_data = obj_in.model_dump(exclude_unset=True)

            # Create ORM model instance
            db_obj = self.orm_model(**create_data)
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
            return self._to_pydantic(db_obj)

    async def update(self, id: UUID, obj_in: Any) -> Optional[T]:
        """Update an existing item."""
        async with self.session_factory() as session:
            db_obj = await session.get(self.orm_model, id)
            if not db_obj:
                return None

            # Convert to dict if needed
            if isinstance(obj_in, dict):
                update_data = obj_in
            else:
                update_data = obj_in.model_dump(exclude_unset=True)

            # Update fields
            for field in update_data:
                if hasattr(db_obj, field):
                    setattr(db_obj, field, update_data[field])

            await session.commit()
            await session.refresh(db_obj)
            return self._to_pydantic(db_obj)

    async def delete(self, id: UUID) -> bool:
        """Delete an item by ID."""
        async with self.session_factory() as session:
            db_obj = await session.get(self.orm_model, id)
            if not db_obj:
                return False

            await session.delete(db_obj)
            await session.commit()
            return True

    async def filter(self, **filters) -> List[T]:
        """Filter items by field values."""
        async with self.session_factory() as session:
            query = select(self.orm_model)

            # Add filter conditions
            for field, value in filters.items():
                if hasattr(self.orm_model, field):
                    query = query.where(getattr(self.orm_model, field) == value)

            result = await session.execute(query)
            orm_models = result.scalars().all()
            return [self._to_pydantic(item) for item in orm_models]

    def _to_pydantic(self, db_obj: ModelType) -> T:
        """Convert ORM model to Pydantic model."""
        return self.pydantic_model.model_validate(db_obj)
