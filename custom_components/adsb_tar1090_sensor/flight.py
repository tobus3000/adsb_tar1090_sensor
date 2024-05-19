"""
FlightData class to build the Home Assistant Sensor data
based on the information received from the ADS-B receiver.

"""
from __future__ import annotations
from .squawk_codes import SQUAWK_CODES

class Flight:
    """Holds details of currently monitored aircraft."""
    def __init__(self, flight_number, flight_data: dict) -> None:
        """Initialize the Aircraft object.

        Args:
            flight_data (dict): A dictionary containing aircraft data.
        """
        self.flight_number = flight_number
        self.data = flight_data
        self.parse_data()

    @property
    def squawk(self) -> tuple|None:
        """Return the squawk code of the aircraft and 
        a squawk code description, if available.

        Returns:
            tuple|None: First entry is Squawk code, second entry is description.
        """
        return self._squawk

    @squawk.setter
    def squawk(self, code: str|None):
        """Set the squawk code of the aircraft.
        This creates a tuple where the first item is the squawk code
        and the second item is the squawk code description.

        Args:
            code (str | None): The squawk code to set.
        """
        if code:
            description = SQUAWK_CODES.get(code)
            self._squawk = (code, description)
        else:
            self._squawk = None

    @property
    def parameters(self) -> tuple:
        """Get altitude and speed.
        This property returns a tuple containing the altitude and speed of the aircraft.

        Returns:
            tuple: A tuple containing the altitude and speed of the aircraft
        """
        return (self._altitude, self._speed)

    @parameters.setter
    def parameters(self, alt_speed_param: tuple) -> None:
        """Set the altitude and speed parameters of the aircraft.

        Args:
            alt_speed_param (tuple): A tuple containing altitude and speed parameters.
        """
        (self._altitude, self._speed) = alt_speed_param

    @property
    def location(self) -> tuple|None:
        """Returns a location tuple for the aircraft.

        Returns:
            tuple|None: A tuple containing the location coordinates (latitude, longitude) 
            of the aircraft, or None if the location is not set.
        """
        return self._location

    @location.setter
    def location(self, location: tuple) -> None:
        """Set the location of the aircraft.
        Takes a tuple of (latitude, longitude).

        Args:
            location (tuple): Tuple of (latitude, longitude)
        """
        if None not in location:
            self._location = location
        else:
            self._location = None

    @property
    def alert(self) -> tuple:
        """Return the alert count and emergency message, if available.
        
         Returns:
            tuple: A tuple containing the alert count and and emergency message.
        """
        return (self._alert, self._emergency)

    @alert.setter
    def alert(self, alert_emergency: tuple) -> None:
        """Set the alert count of the aircraft.
        
        Args:
            alert_emergency (tuple): A tuple containing amount of alerts and an emergency message.
        """
        (self._alert, self._emergency) = alert_emergency

    def parse_data(self):
        """Parses and processes the local ADS-B data."""
        self.squawk = self.data.get("squawk")
        self.flight_number = self.data.get("flight")
        self.parameters = (self.data.get("alt_geom"), self.data.get("mach"))
        self.location = (self.data.get("lat"), self.data.get("lon"))
        self.alert = (self.data.get("alert"), self.data.get("emergency"))
