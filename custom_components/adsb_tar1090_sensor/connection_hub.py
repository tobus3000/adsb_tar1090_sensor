"""Connection Hub class dealing with HTTP calls."""
from __future__ import annotations
import logging
import asyncio
import aiohttp
from homeassistant.exceptions import HomeAssistantError
_LOGGER = logging.getLogger(__name__)

class ConnectionHub:
    """Connection class to verify ADS-B rtl1090 API connection."""

    def __init__(self, endpoint_url) -> None:
        """Initialize."""
        self.url = endpoint_url

    async def fetch_data(self, session):
        """Connects to a URL and returns the JSON data."""
        async with session.get(self.url) as response:
            try:
                response.raise_for_status()
                return await response.json()
            except Exception as exc:
                raise InvalidEndpoint(
                        "Connection to endpoint established but response data is not compatible."
                    ) from exc

    async def test_connect(self) -> bool:
        """Test if we can connect to the API endpoint."""
        try:
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(
                    limit=10,
                    ttl_dns_cache=300
                )
            ) as session:
                data = await self.fetch_data(session)
                if 'aircraft' not in data.keys():
                    raise InvalidEndpoint(
                        "Connection to endpoint established but response data is not compatible."
                        )
        except Exception as exc:
            raise CannotConnect("Failed to connect to endpoint.") from exc
        # Graceful shutdown
        await asyncio.sleep(0)
        return True

class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""

class InvalidEndpoint(HomeAssistantError):
    """Error to indicate that the endpoint is not compatible with this sensor."""
