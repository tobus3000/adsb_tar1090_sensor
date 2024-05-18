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
        """Initialize."""
        self.data = aircraft_data
        self.parse_data()

    @property
    def squawk(self) -> str|None:
        return self._squawk

    @squawk.setter
    def squawk(self, code: str|None):
        self._squawk = code
        if code:
            self.squawk_description = SQUAWK_CODES.get(code)
        else:
            self.squawk_description = None

    @property
    def squawk_description(self) -> str|None:
        return self._squawk_description

    @squawk_description.setter
    def squawk_description(self, description: str|None):
        self._squawk_description = description

    @property
    def flight_number(self) -> str|None:
        return self._flight_number

    @flight_number.setter
    def flight_number(self, number: str|None):
        if number:
            number.rstrip()
        self._flight_number = number

    @property
    def speed_mach(self) -> float|None:
        return self._speed_mach

    @speed_mach.setter
    def speed_mach(self, mach: float|None):
        self._speed_mach = mach

    @property
    def altitude(self) -> int|None:
        return self._altitude

    @altitude.setter
    def altitude(self, altitude_feet: int|None):
        self._altitude = altitude_feet

    @property
    def latitude(self) -> float|None:
        return self._latitude

    @latitude.setter
    def latitude(self, latitude_degrees: float|None):
        self._latitude = latitude_degrees

    @property
    def longitude(self) -> float|None:
        return self._longitude

    @longitude.setter
    def longitude(self, longitude_degrees: float|None):
        self._longitude = longitude_degrees

    @property
    def alert(self) -> int|None:
        return self._alert

    @alert.setter
    def alert(self, alert_count: int|None):
        self._alert = alert_count

    @property
    def emergency(self) -> bool:
        return self._emergency

    @emergency.setter
    def emergency(self, emergency_status: str|None):
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
