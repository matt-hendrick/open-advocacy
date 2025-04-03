import json
import os
from typing import Any, Type, TypeVar
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime
from app.db.base import InMemoryProvider

T = TypeVar("T", bound=BaseModel)


def load_json_data(file_path: str) -> list[dict[str, Any]]:
    """Load data from a JSON file."""
    if not os.path.exists(file_path):
        return []

    with open(file_path, "r") as f:
        return json.load(f)


async def load_data_into_provider(
    provider: InMemoryProvider, model_class: Type[T], data_file: str
) -> None:
    """Load data from a JSON file into an InMemoryProvider."""
    data = load_json_data(data_file)

    for item in data:
        # Convert string IDs to UUID if needed
        if "id" in item and isinstance(item["id"], str):
            item["id"] = UUID(item["id"])

        # Convert string dates to datetime if needed
        for date_field in ["created_at", "updated_at"]:
            if date_field in item and isinstance(item[date_field], str):
                item[date_field] = datetime.fromisoformat(item[date_field])

        await provider.create(item)

    print(f"Loaded {len(data)} items into {model_class.__name__} provider")
