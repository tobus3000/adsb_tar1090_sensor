"""Connection Hub class dealing with HTTP calls."""
from __future__ import annotations
import logging
import asyncio
import aiohttp
from homeassistant.exceptions import HomeAssistantError
#from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .flight_manager import FlightManager
_LOGGER = logging.getLogger(__name__)

class ConnectionHub:
    """Connection class to verify ADS-B tar1090 API connection."""

    def __init__(self, hass, endpoint_url: str) -> None:
        """Initialize."""
        self.hass = hass
        self.url = endpoint_url

    @property
    def url(self) -> str:
        """Returns the endpoint URL.

        Returns:
            str: Endpoint URL
        """
        return self._url

    @url.setter
    def url(self, endpoint_url: str):
        """Stores the endpoint URL.

        Args:
            endpoint_url (str): The URL to the HTTP(s) endpoint.
        """
        self._url = endpoint_url

    @property
    def data(self) -> dict:
        """Returns the http response data as dictionary.

        Returns:
            dict: HTTP response data dictionary.
        """
        return self._data

    @data.setter
    def data(self, response_data: dict):
        """Stores the JSON data from a http(s) response.

        Args:
            response_data (dict): The response JSON data dictionary.
        """
        flight_data = FlightManager(response_data)
        self._data = flight_data.output_data()

    async def async_update(self):
        """The update method that gets called by Home Assistant to refresh the data. """
        try:
            self.data = await self.fetch_data()
        except (
            CannotConnect,
            InvalidData,
            GeneralProblem
         ) as exc:
            _LOGGER.error("Error fetching data: %s", exc)

    async def fetch_data(self) -> dict:
        """Connects to a URL and returns the JSON data."""
        try:
            async with aiohttp.ClientSession() as session:
                response = await session.get(self.url)
                response.raise_for_status()
                return await response.json()
        except (
            asyncio.TimeoutError,
            aiohttp.ClientConnectionError,
            aiohttp.ClientSSLError,
            aiohttp.ClientConnectorSSLError,
            aiohttp.ServerConnectionError,
            aiohttp.ServerTimeoutError
        ) as exc:
            _LOGGER.error("Error connecting to ADS-B receiver endpoint: %s", exc)
            raise CannotConnect(
                "Cannot establish connection."
            ) from exc
        except (
            aiohttp.ClientPayloadError,
            aiohttp.ContentTypeError,
            aiohttp.ClientResponseError
        ) as exc:
            _LOGGER.error("Problem with the payload from the ADS-B receiver endpoint: %s", exc)
            raise InvalidData(
                "There is a problem with the payload."
            ) from exc
        except (
            Exception,
            aiohttp.ClientError
            ) as exc:
            _LOGGER.error("General error connecting to ADS-B receiver endpoint: %s", exc)
            raise GeneralProblem(
                    "General error connecting to ADS-B receiver endpoint"
                ) from exc

    async def test_connect(self) -> bool:
        """Test if we can connect to the API endpoint."""
        try:
            data = await self.fetch_data()
            _LOGGER.debug("ADS-B Data: %s", data)
            if 'aircraft' not in data.keys():
                raise InvalidData(
                    "Connection to endpoint established but response data is not compatible."
                    )
        except Exception as exc:
            raise CannotConnect("Failed to connect to endpoint.") from exc
        # Graceful shutdown
        await asyncio.sleep(0)
        return True

class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""

class InvalidData(HomeAssistantError):
    """Error when the response of a GET request is not what we expect."""

class GeneralProblem(HomeAssistantError):
    """Error to indicate that the endpoint is not compatible with this sensor."""
