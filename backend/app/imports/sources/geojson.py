from typing import Any
import json
import aiohttp
import logging
from pathlib import Path
from tempfile import NamedTemporaryFile

from app.imports.base import DataSource

logger = logging.getLogger(__name__)


class GeoJSONDataSource(DataSource):
    """Data source for GeoJSON district boundaries."""

    def __init__(
        self,
        file_path: str | None = None,
        url: str | None = None,
        stream_threshold: int = 10 * 1024 * 1024,  # 10 MB
    ):
        """
        Initialize GeoJSON data source.

        Args:
            file_path: Path to local GeoJSON file
            url: URL to download GeoJSON from
            stream_threshold: File size threshold for streaming downloads (in bytes)
        """
        if not file_path and not url:
            raise ValueError("Either file_path or url must be provided")

        self.file_path = file_path
        self.url = url
        self.stream_threshold = stream_threshold
        self._temp_file = None

    async def fetch_data(self) -> dict[str, Any]:
        """Read GeoJSON data from file or URL."""
        if self.file_path:
            return await self._read_local_file()
        else:
            return await self._download_from_url()

    async def _read_local_file(self) -> dict[str, Any]:
        """Read GeoJSON data from local file."""
        try:
            with open(self.file_path, "r") as f:
                data = json.load(f)
                self._validate_geojson(data)
                return data
        except Exception as e:
            raise Exception(f"Error reading GeoJSON file: {str(e)}")

    async def _download_from_url(self) -> dict[str, Any]:
        """Download GeoJSON data from URL."""
        async with aiohttp.ClientSession() as session:
            # First check the content length to decide if we need to stream
            async with session.head(self.url) as head_response:
                if head_response.status != 200:
                    raise Exception(f"Failed to access URL: {head_response.status}")

                content_length = int(head_response.headers.get("Content-Length", "0"))

                # Use streaming for large files
                if content_length > self.stream_threshold:
                    return await self._stream_download(session)

                # For smaller files, download directly
                async with session.get(self.url) as response:
                    if response.status != 200:
                        raise Exception(
                            f"Failed to download from URL: {response.status}"
                        )

                    data = await response.json()
                    self._validate_geojson(data)
                    return data

    async def _stream_download(self, session: aiohttp.ClientSession) -> dict[str, Any]:
        """Stream download large GeoJSON files to avoid memory issues."""
        # Create a temporary file
        self._temp_file = NamedTemporaryFile(delete=False, suffix=".geojson")
        temp_path = self._temp_file.name

        try:
            # Stream the download to the temp file
            logger.info(f"Streaming large GeoJSON file to {temp_path}")

            async with session.get(self.url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to download from URL: {response.status}")

                with open(temp_path, "wb") as f:
                    chunk_size = 8192  # 8KB chunks
                    downloaded = 0

                    while True:
                        chunk = await response.content.read(chunk_size)
                        if not chunk:
                            break

                        f.write(chunk)
                        downloaded += len(chunk)

                        if downloaded % (5 * 1024 * 1024) == 0:  # Log every 5MB
                            logger.info(
                                f"Downloaded {downloaded / (1024 * 1024):.1f} MB"
                            )

            # Read the file
            with open(temp_path, "r") as f:
                data = json.load(f)
                self._validate_geojson(data)
                return data

        except Exception as e:
            raise Exception(f"Error streaming GeoJSON file: {str(e)}")
        finally:
            # Clean up the temp file
            try:
                Path(temp_path).unlink(missing_ok=True)
            except Exception:
                pass

    def _validate_geojson(self, data: dict[str, Any]) -> None:
        """Validate that the data is a GeoJSON FeatureCollection."""
        if not isinstance(data, dict):
            raise ValueError("Invalid GeoJSON: Not a dictionary")

        if data.get("type") != "FeatureCollection":
            raise ValueError("Invalid GeoJSON: Not a FeatureCollection")

        if "features" not in data or not isinstance(data["features"], list):
            raise ValueError("Invalid GeoJSON: No features array found")

    def get_source_info(self) -> dict[str, Any]:
        """Get information about the data source."""
        if self.file_path:
            source = f"Local file: {self.file_path}"
        else:
            source = f"URL: {self.url}"

        return {
            "name": "GeoJSON District Boundaries",
            "source": source,
            "type": "GeoJSON",
            "description": "GeoJSON boundaries for electoral districts",
        }

    def __del__(self):
        """Clean up any temporary files on object destruction."""
        if self._temp_file:
            try:
                Path(self._temp_file.name).unlink(missing_ok=True)
            except Exception:
                pass
