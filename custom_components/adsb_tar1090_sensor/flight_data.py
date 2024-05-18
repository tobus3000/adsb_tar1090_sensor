"""
FlightData class to build the Home Assistant Sensor data
based on the information received from the ADS-B receiver.

"""
from __future__ import annotations
import logging
import haversine
from homeassistant.exceptions import HomeAssistantError
from .squawk_codes import SQUAWK_CODES
_LOGGER = logging.getLogger(__name__)

class FlightData:
    """Connection class to verify ADS-B rtl1090 API connection."""

    def __init__(self, adsb_data: dict) -> None:
        """Initialize."""
        self.adsb_data = adsb_data

    @property
    def adsb_data(self) -> dict:
        return self._adsb_data
    
    @adsb_data.setter
    def adsb_data(self, data: dict):
        self._adsb_data = data
        self.message_count = data.get('messages',0)

    @property
    def message_count(self) -> int:
        return self._message_count

    @message_count.setter
    def message_count(self, count: int):
        if isinstance(count, int):
            self._message_count = count
        else:
            self._message_count = 0

    def output_data(self) -> dict:
        return self.adsb_data

    @staticmethod
    async def haversine_distance(coord1: tuple, coord2: tuple) -> float:
        """
        Calculate the haversine distance between two geographic coordinates.

        Haversine distance is a formula used to calculate the distance between two points
        on the surface of a sphere given their longitudes and latitudes. It's commonly
        used in geographic applications for calculating distances between locations.

        Parameters:
            coord1 (tuple): A tuple containing the latitude and longitude of the first coordinate in degrees.
            coord2 (tuple): A tuple containing the latitude and longitude of the second coordinate in degrees.

        Returns:
            float: The haversine distance between the two coordinates in kilometers, rounded to two decimal places.
        """
        distance_km = haversine.haversine(coord1, coord2)
        return round(distance_km,2)

