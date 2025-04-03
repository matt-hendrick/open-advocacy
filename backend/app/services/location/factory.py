from typing import Dict, Type
from app.services.location.base import LocationModule
from app.services.location.default import DefaultLocationModule

# Registry of available location modules
_location_modules: Dict[str, Type[LocationModule]] = {
    "default": DefaultLocationModule,
}


def register_location_module(id: str, module_class: Type[LocationModule]):
    """Register a new location module."""
    _location_modules[id] = module_class


def get_location_module(id: str) -> LocationModule:
    """Get a location module by ID."""
    module_class = _location_modules.get(id, DefaultLocationModule)
    return module_class()


def list_available_modules() -> Dict[str, str]:
    """List all available location modules."""
    return {id: module.__name__ for id, module in _location_modules.items()}
