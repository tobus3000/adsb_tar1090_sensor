"""
FlightData class to build the Home Assistant Sensor data
based on the information received from the ADS-B receiver.

"""
from __future__ import annotations
import logging
from .squawk_codes import SQUAWK_CODES
_LOGGER = logging.getLogger(__name__)

class Aircraft:
    """Holds details of currently monitored aircraft."""
    def __init__(self, aircraft_data: dict) -> None:
        """Initialize the Aircraft object.

        Args:
            aircraft_data (dict): A dictionary containing aircraft data.
        """
        self.data = aircraft_data
        self.parse_data()

    @property
    def squawk(self) -> str|None:
        """Return the squawk code of the aircraft, if available."""
        return self._squawk

    @squawk.setter
    def squawk(self, code: str|None):
        """Set the squawk code of the aircraft.

        Args:
            code (str | None): The squawk code to set.
        """
        self._squawk = code
        if code:
            self.squawk_description = SQUAWK_CODES.get(code)
        else:
            self.squawk_description = None

    @property
    def squawk_description(self) -> str|None:
        """Return the description of the squawk code, if available."""
        return self._squawk_description

    @squawk_description.setter
    def squawk_description(self, description: str|None):
        """Set the description of the squawk code.

        Args:
            description (str | None): The description to set.
        """
        self._squawk_description = description

    @property
    def flight_number(self) -> str|None:
        """Return the flight number of the aircraft, if available."""
        return self._flight_number

    @flight_number.setter
    def flight_number(self, number: str|None):
        """Set the flight number of the aircraft.

        Args:
            number (str | None): The flight number to set.
        """
        if number:
            number.rstrip()
        self._flight_number = number

    @property
    def speed_mach(self) -> float|None:
        """Return the speed of the aircraft in Mach, if available."""
        return self._speed_mach

    @speed_mach.setter
    def speed_mach(self, mach: float|None):
        """Set the speed of the aircraft in Mach.

        Args:
            mach (float | None): The speed in Mach to set.
        """
        self._speed_mach = mach

    @property
    def altitude(self) -> int|None:
        """Return the altitude of the aircraft, if available."""
        return self._altitude

    @altitude.setter
    def altitude(self, altitude_feet: int|None):
        """Set the altitude of the aircraft.

        Args:
            altitude_feet (int | None): The altitude in feet to set.
        """
        self._altitude = altitude_feet

    @property
    def latitude(self) -> float|None:
        """Return the latitude of the aircraft, if available."""
        return self._latitude

    @latitude.setter
    def latitude(self, latitude_degrees: float|None):
        """Set the latitude of the aircraft.

        Args:
            latitude_degrees (float | None): The latitude in degrees to set.
        """
        self._latitude = latitude_degrees

    @property
    def longitude(self) -> float|None:
        """Return the longitude of the aircraft, if available."""
        return self._longitude

    @longitude.setter
    def longitude(self, longitude_degrees: float|None):
        """Set the longitude of the aircraft.

        Args:
            longitude_degrees (float | None): The longitude in degrees to set.
        """
        self._longitude = longitude_degrees

    @property
    def alert(self) -> int|None:
        """Return the alert count of the aircraft, if available."""
        return self._alert

    @alert.setter
    def alert(self, alert_count: int|None):
        """Set the alert count of the aircraft.

        Args:
            alert_count (int | None): The alert count to set.
        """
        self._alert = alert_count

    @property
    def emergency(self) -> bool:
        """Return the emergency status of the aircraft."""
        return self._emergency

    @emergency.setter
    def emergency(self, emergency_status: str|bool|None):
        """Set the emergency status of the aircraft.

        Args:
            emergency_status (str | bool | None): The emergency status to set.
        """
        if emergency_status:
            self._emergency = True
        else:
            self._emergency = False

    def parse_data(self):
        """Parses and processes the local ADS-B data."""
        self.squawk = self.data.get("squawk")
        self.flight_number = self.data.get("flight")
        self.speed_mach = self.data.get("mach")
        self.altitude = self.data.get("alt_geom")
        self.latitude = self.data.get("lat")
        self.longitude = self.data.get("lon")
        self.alert = self.data.get("alert")
        self.emergency = self.data.get("emergency")
