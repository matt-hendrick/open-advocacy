from typing import Tuple
import httpx
from fastapi import HTTPException
from app.core.config import settings


class GeocodingService:
    """Service for geocoding addresses to coordinates"""

    async def geocode_address(self, address: str) -> Tuple[float, float]:
        """
        Convert address to coordinates

        Args:
            address: Address string

        Returns:
            Tuple of (latitude, longitude)
        """
        # Use commercial service if configured
        if settings.GEOCODING_SERVICE and settings.GEOCODING_API_KEY:
            return await self._geocode_commercial(address)
        else:
            # Fall back to Nominatim
            return await self._geocode_nominatim(address)

    async def _geocode_nominatim(self, address: str) -> Tuple[float, float]:
        """Use Nominatim/OpenStreetMap for geocoding (free)"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={
                        "q": address,
                        "format": "json",
                        "limit": 1,
                    },
                    headers={"User-Agent": "open-advocacy-platform"},
                    timeout=10.0,
                )

                if response.status_code != 200:
                    raise HTTPException(
                        status_code=500, detail="Geocoding service error"
                    )

                results = response.json()
                if not results:
                    raise HTTPException(status_code=404, detail="Address not found")

                lat = float(results[0]["lat"])
                lon = float(results[0]["lon"])
                return (lat, lon)

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Geocoding error: {str(e)}")

    async def _geocode_commercial(self, address: str) -> Tuple[float, float]:
        """Use commercial geocoding service if configured"""
        # TODO: Implement geocoding using Google Maps
        # Stub of a function below

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://maps.googleapis.com/maps/api/geocode/json",
                    params={"address": address, "key": settings.GEOCODING_API_KEY},
                    timeout=10.0,
                )

                data = response.json()

                if data["status"] != "OK":
                    raise HTTPException(
                        status_code=500, detail=f"Geocoding error: {data['status']}"
                    )

                location = data["results"][0]["geometry"]["location"]
                return (location["lat"], location["lng"])

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Geocoding error: {str(e)}")
