from typing import Any
from app.imports.base import DataSource
import aiohttp


class ChicagoAlderpersonDataSource(DataSource):
    """Data source for Chicago alderpersons."""

    def __init__(
        self, api_url: str = "https://data.cityofchicago.org/resource/c6ie-9e6c.json"
    ):
        self.api_url = api_url

    async def fetch_data(self) -> list[dict[str, Any]]:
        """Fetch aldermen data from the Chicago API."""
        async with aiohttp.ClientSession() as session:
            async with session.get(self.api_url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Failed to fetch data: {response.status}")

    def get_source_info(self) -> dict[str, Any]:
        """Get information about the data source."""
        return {
            "name": "Chicago Alderperson Data",
            "url": self.api_url,
            "type": "REST API",
            "description": "Official City of Chicago data on alderpersons",
        }
