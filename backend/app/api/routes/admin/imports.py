from fastapi import APIRouter, HTTPException, Depends
from typing import Any

from app.imports.orchestrator import ImportOrchestrator
from app.models.pydantic.models import User
from app.core.auth import get_super_admin_user
from app.imports.locations.chicago import ChicagoLocationConfig
from app.imports.locations.illinois import IllinoisLocationConfig


router = APIRouter()

# Register available locations
orchestrator = ImportOrchestrator()
orchestrator.register_location("chicago", ChicagoLocationConfig)
orchestrator.register_location("illinois", IllinoisLocationConfig)


@router.get("/locations", response_model=list[dict[str, Any]])
async def list_locations(current_user: User = Depends(get_super_admin_user)):
    """List available locations for import. Only accessible by super admins."""
    return await orchestrator.get_available_locations()


@router.post("/locations/{location_key}", response_model=dict[str, Any])
async def import_location(
    location_key: str,
    override_params: dict[str, Any] | None = None,
    current_user: User = Depends(get_super_admin_user),
):
    """Import data for a specific location. Only accessible by super admins."""
    try:
        params = override_params or {}
        result = await orchestrator.import_location(location_key, **params)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")
