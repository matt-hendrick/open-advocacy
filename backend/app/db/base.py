from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Any, Type

T = TypeVar("T")
ID = TypeVar("ID")


class DatabaseProvider(ABC, Generic[T, ID]):
    @abstractmethod
    async def get(self, id: ID) -> T | None:
        pass

    @abstractmethod
    async def list(self, skip: int = 0, limit: int = 100) -> list[T]:
        pass

    @abstractmethod
    async def create(self, obj_in: Any) -> T:
        pass

    @abstractmethod
    async def update(self, id: ID, obj_in: Any) -> T | None:
        pass

    @abstractmethod
    async def delete(self, id: ID) -> bool:
        pass


class InMemoryProvider(Generic[T, ID]):
    """In-memory implementation of database provider."""

    def __init__(self, model_class: Type[T]):
        self.data: dict[ID, T] = {}
        self.model_class = model_class

    async def get(self, id: ID) -> T | None:
        return self.data.get(id)

    async def list(self, skip: int = 0, limit: int = 100) -> list[T]:
        return list(self.data.values())[skip : skip + limit]

    async def create(self, obj_in: Any) -> T:
        if isinstance(obj_in, dict):
            obj = self.model_class(**obj_in)
        else:
            obj = self.model_class(**obj_in.dict())

        self.data[obj.id] = obj
        return obj

    async def update(self, id: ID, obj_in: Any) -> T | None:
        if id not in self.data:
            return None

        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        obj = self.data[id]
        for field in update_data:
            if hasattr(obj, field):
                setattr(obj, field, update_data[field])

        self.data[id] = obj
        return obj

    async def delete(self, id: ID) -> bool:
        if id in self.data:
            del self.data[id]
            return True
        return False
