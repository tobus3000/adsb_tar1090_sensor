"""The Sensor class and definitions."""
import logging
from typing import Any, Dict, List, Optional
import asyncio
from datetime import timedelta
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    EntityCategory
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .utils import generate_entity_id
from .connection_hub import ConnectionHub
from .const import (
    CONF_URL,
    DOMAIN
)

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(minutes=5)
SENSOR_PAYLOAD_KEYS = {
    #'alert': ['squawk', 'distance', 'flight'],
    'statistics': [
        'monitored_flights',
        'nearest_flight',
        'nearest_flight_distance',
        'nearest_flight_altitude',
        'nearest_flight_speed',
        'message_count',
        'emergencies'
    ]
}

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities
):
    """Setup sensors from a config entry created in the integration UI.

    Args:
        hass (HomeAssistant): _description_
        config (Dict[str, Any]): _description_
        async_add_entities (_type_): _description_
    """
    config = hass.data[DOMAIN][config_entry.entry_id]
    url = config[CONF_URL]
    session = ConnectionHub(hass, url)
    sensors = []
    for sensor_name, payload_keys in SENSOR_PAYLOAD_KEYS.items():
        sensors.append(ADSBTar1090Sensor(hass, sensor_name, session, payload_keys))
    async_add_entities(sensors, update_before_add=True)

# async def async_setup_platform(
#     hass: HomeAssistant,
#     config: Dict[str, Any],
#     async_add_entities,
#     discovery_info: Optional[Dict[str, Any]] = None
# ) -> None:
#     """Set up the sensor platform for the custom component.
#     This function is responsible for setting up the sensor platform within the custom component.
#     Called when Home Assistant discovers and initializes the sensor platform based on configuration.

#     Args:
#         hass (HomeAssistant): The Home Assistant core instance.
#         config (Dict[str, Any]): The configuration for the sensor platform.
#         async_add_entities (Callable[[List[Entity], bool]): A function to add entities to HA.
#         discovery_info (Optional[Dict[str, Any]]): Optional discovery information. Defaults to None.
#     """
#     if discovery_info is None:
#         _LOGGER.debug("No discovery info available.")
#     url = config[DOMAIN][CONF_URL]
#     rest_data = ConnectionHub(hass, url)

#     entities = []
#     for sensor_name, payload_keys in SENSOR_PAYLOAD_KEYS.items():
#         entities.append(ADSBTar1090Sensor(hass, sensor_name, rest_data, payload_keys))

#     if entities:
#         await rest_data.async_update()
#         async_add_entities(entities)


async def async_update_entities(entities: list):
    """Asynchronously updates the state of multiple entities at specified intervals.

    This function iterates indefinitely, updating the state of each entity in the provided list
    at intervals determined by the SCAN_INTERVAL constant.

    Args:
        entities (list): A list of Entity objects whose state needs to be updated.
    """
    while True:
        await asyncio.sleep(SCAN_INTERVAL.total_seconds())
        await asyncio.gather(*[entity.async_update() for entity in entities])


class ADSBTar1090Sensor(SensorEntity):
    """Representation of a sensor for ADS-B data retrieved from tar1090 API."""
    _attr_entity_category = (
        EntityCategory.DIAGNOSTIC
    )
    def __init__(
        self,
        hass: HomeAssistant,
        name: str,
        rest_data: ConnectionHub,
        payload_keys: List[str]
    ) -> None:
        """Initialize the ADS-B sensor.

        Args:
            hass (HomeAssistant): The Home Assistant core instance.
            name (str): Name of the sensor.
            rest_data (ConnectionHub): ConnectionHub instance for fetching data.
            payload_keys (List[str]): List of keys in the payload representing sensor data.
        """
        self._hass = hass
        self._name = name
        self._attr_unique_id = generate_entity_id(DOMAIN, name)
        self._rest_data = rest_data
        self._payload_keys = payload_keys
        self._state = {key: None for key in payload_keys}

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    async def async_update(self):
        """Update the sensor state."""
        _LOGGER.debug("ADS-B tar1090 Sensor: Updating Sensors.")
        await self._rest_data.async_update()
        data = self._rest_data.data
        if data:
            for key in self._payload_keys:
                if key in data:
                    self._state[key] = data[key]
