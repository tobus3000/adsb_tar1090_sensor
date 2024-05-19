"""
FlightManager class to track all current flights based
on the information received from the ADS-B receiver.

"""
from __future__ import annotations
import logging
import haversine
from homeassistant.const import (
    ATTR_LATITUDE,
    ATTR_LONGITUDE
    )
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from .flight import Flight
_LOGGER = logging.getLogger(__name__)

class FlightManager:
    """Connection class to verify ADS-B tar1090 API connection."""

    def __init__(self, hass: HomeAssistant, adsb_data: dict) -> None:
        """Initialize the FlightData class.

        Args:
            hass (HomeAssistant): The Home Assistance object instance.
            adsb_data (dict): The `aircraft.json` response data.
        """
        self.hass = hass
        self.location = self.get_location()
        self.active_flights = {}
        self.adsb_data = adsb_data
        self.distances = {}
        self.emergencies = {}

    @property
    def adsb_data(self) -> dict:
        """Returns the `aircraft.json` response data.

        Returns:
            dict: The `aircraft.json` response data.
        """
        return self._adsb_data

    @adsb_data.setter
    def adsb_data(self, data: dict):
        self._adsb_data = data
        self.parse_adsb_data()

    @property
    def message_count(self) -> int:
        """Returns the current ADS-B message counts.

        Returns:
            int: Amount of ADS-B messages processed by the endpoint.
        """
        return self._message_count

    @message_count.setter
    def message_count(self, count: int):
        if not isinstance(count, int):
            count = 0
        self._message_count = count

    def parse_adsb_data(self):
        """Parses and processes the local ADS-B data.

        Raises:
            DataParserError: Failed to parse the aircraft data.
        """
        self.message_count = self.adsb_data.get('messages',0)
        self.extract_flight_data()
        self.calculate_distances()
        self.analyze_squawk()

    def extract_flight_data(self):
        """Extract the aircraft data from the ADS-B data.
           Process each flight and update the class property values.
        """
        aircrafts = self.adsb_data.get("aircraft")
        if aircrafts:
            for flight_data in aircrafts:
                flight_number = flight_data.get("flight", "").rstrip()
                if flight_number != "":
                    self.add_flight(flight_number, flight_data)
        else:
            raise DataParserError("Failed to parse the aircraft data.")

    def calculate_distances(self):
        """Iterates over all current flights and calculates the distance (in km) between
        the flight and your position.
        """
        for flight in self.get_all_flights():
            if flight.location and self.location:
                distance = FlightManager.haversine_distance(self.location, flight.location)
                if distance and isinstance(distance, float):
                    self.distances[flight.flight_number] = distance

    def analyze_squawk(self):
        """Iterates over all current flights and searches for flights with an emergency
        transponder code set.
        """
        for flight in self.get_all_flights():
            if flight.squawk:
                (code, description) = flight.squawk
                #TODO: get emergency squawk from configuration.
                if code in [7500,7600,7700]:
                    _LOGGER.debug(
                        "Flight %s has set emergency squawk code %s - %s!",
                        flight.flight_number,
                        code,
                        description
                    )
                    self.emergencies[flight.flight_number] = flight.squawk

    def add_flight(self, flight_number: str, flight_data: dict) -> None:
        """Adds a Flight object to the list of active flights.

        Args:
            flight_number (str): The flight number, such as 'AFR564' or similar.
            flight_data (dict): A single item from the list of dicts under
            the `aircraft` key inside `aircraft.json`.
        """
        flight = Flight(flight_number, flight_data)
        self.active_flights[flight_number] = flight

    def remove_flight(self, flight_number: str) -> None:
        """Removes a flight from the list of active flights.

        Args:
            flight_number (str): The flight number, such as 'AFR564' or similar.
        """
        if flight_number in self.active_flights:
            del self.active_flights[flight_number]

    def get_flight(self, flight_number: str) -> Flight | None:
        """Get flight by flight number

        Args:
            flight_number (str): The flight number, such as 'AFR564' or similar.

        Returns:
            Flight | None: `Flight` object instance or None if no flight has been found.
        """
        return self.active_flights.get(flight_number)

    def get_all_flights(self) -> list:
        """Get all active flights as a list

        Returns:
            list: All active flights as a list of `Flight` object instances.
        """
        return list(self.active_flights.values())

    def output_data(self) -> dict:
        """Returns the output data required by the Home Assistant ADS-B Sensor.

        #TODO: add last_emergency_flight_within_thold, last_emergency_flight, request_time,
        # nearest_flight, total_flights_monitored, messages_received

        Returns:
            dict: Sensor data for further processing.
        """
        return {
            "message_count": self.message_count,
            "monitored_flights": len(self.active_flights),
            "emergencies": len(self.emergencies),
            "nearest_flight": min(self.distances.values())
        }

    @staticmethod
    def haversine_distance(coord1: tuple, coord2: tuple) -> float:
        """
        Calculate the haversine distance between two geographic coordinates.

        Haversine distance is a formula used to calculate the distance between two points
        on the surface of a sphere given their longitudes and latitudes. It's commonly
        used in geographic applications for calculating distances between locations.

        Parameters:
            coord1 (tuple): The latitude and longitude of the first coordinate in degrees.
            coord2 (tuple): The latitude and longitude of the second coordinate in degrees.

        Returns:
            float: The haversine distance between the two coordinates in kilometers,
            rounded to two decimal places.
        """
        distance_km = haversine.haversine(coord1, coord2)
        return round(distance_km,2)

    def get_location(self) -> tuple | None:
        """Retrieve the latitude and longitude of the Home Assistant installation.

        This function asynchronously fetches the latitude and longitude attributes 
        of the "sun.sun" entity, which typically represents the location of the 
        Home Assistant installation.

        Returns:
            tuple | None: A tuple containing the latitude and longitude of the Home Assistant 
            installation. If the location is not available, None is returned.
        """
        states = self.hass.states.async_all()
        latitude = next(
            (
                state.attributes.get(ATTR_LATITUDE)
                for state in states
                if state.entity_id == "sun.sun"
            ),
            None
        )
        longitude = next(
            (
                state.attributes.get(ATTR_LONGITUDE)
                for state in states
                if state.entity_id == "sun.sun"
            ),
            None
        )
        if latitude and longitude:
            return (latitude, longitude)
        else:
            return None

class DataParserError(HomeAssistantError):
    """Error to indicate that data could not be parsed."""
