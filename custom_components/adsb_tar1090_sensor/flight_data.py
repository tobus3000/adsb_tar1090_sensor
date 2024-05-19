"""
FlightData class to build the Home Assistant Sensor data
based on the information received from the ADS-B receiver.

"""
from __future__ import annotations
import haversine
from homeassistant.exceptions import HomeAssistantError
from .aircraft import Aircraft

class FlightData:
    """Connection class to verify ADS-B tar1090 API connection."""

    def __init__(self, adsb_data: dict) -> None:
        """Initialize the FlightData class.

        Args:
            adsb_data (dict): The `aircraft.json` response data.
        """
        self.message_count = 0
        self.monitored_flights = 0
        self.alerts = 0
        self.adsb_data = adsb_data

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

    @property
    def monitored_flights(self) -> int:
        """Returns the amount of flights currently monitored by your ADS-B receiver.

        Returns:
            int: Current amount of flights monitored.
        """
        return self._monitored_flights

    @monitored_flights.setter
    def monitored_flights(self, count: int):
        if not isinstance(count, int):
            count = 0
        self._monitored_flights = count

    @property
    def alerts(self) -> int:
        """Returns the amount of currently tracked alerts.

        Returns:
            int: Current alert count
        """
        return self._alerts

    @alerts.setter
    def alerts(self, count: int):
        """Set the current alert count.

        Args:
            count (int): The current alert count
        """
        if not isinstance(count, int):
            count = 0
        self._alerts = count

    def parse_adsb_data(self):
        """Parses and processes the local ADS-B data.

        Raises:
            DataParserError: Failed to parse the aircraft data.
        """
        self.message_count = self.adsb_data.get('messages',0)
        self.extract_aircraft_data()

    def extract_aircraft_data(self):
        """Extract the aircraft data from the ADS-B data.
           Process each flight and update the class property values.

        Returns:
            bool: _description_
        """
        aircrafts = self.adsb_data.get("aircraft")
        if aircrafts:
            self.monitored_flights = len(aircrafts)
            for aircraft_data in aircrafts:
                data = Aircraft(aircraft_data)
                if data.emergency:
                    self.alerts=self.alerts + 1
                # squawk = aircraft.get("squawk")
                # # skip record when no SQUAWK code is set.
                # if not squawk:
                #     continue
                # flight = aircraft.get("flight")
                # # skip record when no flight number is set.
                # if not flight:
                #     continue
                # # get latitude & longitude
                # lat = aircraft.get("lat")
                # lon = aircraft.get("lon")
                # # skip if no location data is present.
                # if not lat or not lon:
                #     continue

        else:
            raise DataParserError("Failed to parse the aircraft data.")

    def output_data(self) -> dict:
        """Returns the output data required by the Home Assistant ADS-B Sensor.

        #TODO: add last_emergency_flight_within_thold, last_emergency_flight, request_time,
        # nearest_flight, total_flights_monitored, messages_received

        Returns:
            dict: Sensor data for further processing.
        """
        return {
            "message_count": self.message_count,
            "monitored_flights": self.monitored_flights,
            "alerts": self.alerts
        }

    @staticmethod
    async def haversine_distance(coord1: tuple, coord2: tuple) -> float:
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


class DataParserError(HomeAssistantError):
    """Error to indicate that data could not be parsed."""
