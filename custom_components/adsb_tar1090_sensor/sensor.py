"""The Sensor class and definitions."""
import logging
import json
import aiohttp
import asyncio
import async_timeout

from datetime import timedelta
from homeassistant.helpers.entity import Entity
from homeassistant.const import (
    CONF_NAME
)
from .connection_hub import (
    ConnectionHub,
    CannotConnect
)
from .const import (
    DOMAIN,
    CONF_URL,
    CONF_SENSORS
)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=5)

# CONFIG_SCHEMA = vol.Schema({
#     DOMAIN: vol.Schema({
#         vol.Required(CONF_URL): cv.string
#     }),
# }, extra=vol.ALLOW_EXTRA)


async def async_setup(hass, config):
    url = config[DOMAIN][CONF_URL]
    sensors = config[DOMAIN][CONF_SENSORS]
    
    rest_data = ConnectionHub(hass, url)

    entities = []
    for sensor_name, payload_key in sensors.items():
        entities.append(ADSBRtl1090Sensor(hass, sensor_name, rest_data, payload_key))

    if entities:
        hass.async_create_task(rest_data.async_update())
        hass.async_create_task(async_update_entities(entities))

    return True


async def async_update_entities(entities):
    """
    Asynchronously updates the state of multiple entities at specified intervals.

    This function iterates indefinitely, updating the state of each entity in the provided list
    at intervals determined by the SCAN_INTERVAL constant.

    Parameters:
        entities (list of Entity): A list of Entity objects whose state needs to be updated.

    Returns:
        None

    Notes:
        - The function indefinitely iterates using a while loop, sleeping for the duration 
          specified by SCAN_INTERVAL between updates.
        - Upon each iteration, it concurrently updates the state of all entities in the list
          using asyncio.gather(), ensuring that the updates are performed efficiently in parallel.
    """
    while True:
        await asyncio.sleep(SCAN_INTERVAL.total_seconds())
        await asyncio.gather(*[entity.async_update() for entity in entities])


class ADSBRtl1090Sensor(Entity):
    def __init__(self, hass, name, rest_data, payload_key):
        self._hass = hass
        self._name = name
        self._rest_data = rest_data
        self._payload_key = payload_key
        self._state = None

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def unit_of_measurement(self):
        # Add appropriate unit of measurement based on your data
        #TODO: add last_emergency_flight_within_thold, last_emergency_flight, request_time, nearest_flight, total_flights_monitored, messages_received
        if self._payload_key == 'nearest_flight':
            return 'km'
        elif self._payload_key == 'humidity':
            return '%'
        else:
            return None

    async def async_update(self):
        await self._rest_data.async_update()
        data = self._rest_data.data
        if data:
            self._state = data.get(self._payload_key)

