from fastapi import APIRouter, HTTPException
from typing import Any

from app.imports.orchestrator import ImportOrchestrator

router = APIRouter()

# Register available locations
from app.imports.locations.chicago import ChicagoLocationConfig
# from app.imports.locations.illinois import IllinoisLocationConfig

orchestrator = ImportOrchestrator()
orchestrator.register_location("chicago", ChicagoLocationConfig)
# orchestrator.register_location("illinois", IllinoisLocationConfig)


# TODO: Add auth system and a depends function to validate the user has permissions
@router.get("/locations", response_model=list[dict[str, Any]])
async def list_locations():
    """List available locations for import."""
    return await orchestrator.get_available_locations()


# TODO: Add auth system and a depends function to validate the user has permissions
@router.post("/locations/{location_key}", response_model=dict[str, Any])
async def import_location(
    location_key: str,
    override_params: dict[str, Any] | None = None,
):
    """Import data for a specific location."""
    try:
        params = override_params or {}
        result = await orchestrator.import_location(location_key, **params)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")
