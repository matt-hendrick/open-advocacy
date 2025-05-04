from uuid import UUID

from app.models.pydantic.models import Group, GroupBase
from app.db.base import DatabaseProvider


class GroupService:
    def __init__(
        self,
        groups_provider: DatabaseProvider,
    ):
        self.groups_provider = groups_provider

    async def list_groups(self) -> list[Group]:
        """List all groups."""
        return await self.groups_provider.list()

    async def create_group(self, group: GroupBase) -> Group:
        """Create a new group."""
        return await self.groups_provider.create(group)

    async def get_group(self, group_id: UUID) -> Group | None:
        """Get a group by ID."""
        return await self.groups_provider.get(group_id)

    async def update_group(self, group_id: UUID, group: GroupBase) -> Group | None:
        """Update an existing group."""
        existing_group = await self.groups_provider.get(group_id)
        if not existing_group:
            return None

        return await self.groups_provider.update(group_id, group)

    async def delete_group(self, group_id: UUID) -> bool:
        """Delete a group by ID."""
        existing_group = await self.groups_provider.get(group_id)
        if not existing_group:
            return False

        return await self.groups_provider.delete(group_id)
