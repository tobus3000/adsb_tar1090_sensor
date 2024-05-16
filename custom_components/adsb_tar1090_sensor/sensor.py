import logging
import json
import aiohttp
import asyncio
import async_timeout

from datetime import timedelta
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.const import (
    CONF_NAME
)
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
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
    session = async_get_clientsession(hass)

    rest_data = ReceiverData(hass, session, url)

    entities = []
    for sensor_name, payload_key in sensors.items():
        entities.append(ADSBRtl1090Sensor(hass, sensor_name, rest_data, payload_key))

    if entities:
        hass.async_create_task(rest_data.async_update())
        hass.async_create_task(async_update_entities(entities))

    return True


async def async_update_entities(entities):
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
        if self._payload_key == 'temperature':
            return '°C'
        elif self._payload_key == 'humidity':
            return '%'
        else:
            return None

    async def async_update(self):
        await self._rest_data.async_update()
        data = self._rest_data.data
        if data:
            self._state = data.get(self._payload_key)


class ReceiverData:
    def __init__(self, hass, session, url):
        self._hass = hass
        self._session = session
        self._url = url
        self._data = {}

    @property
    def data(self):
        return self._data

    async def async_update(self):
        try:
            with async_timeout.timeout(10):
                response = await self._session.get(self._url)
                response.raise_for_status()
                self._data = await response.json()
        except (asyncio.TimeoutError, aiohttp.ClientError) as ex:
            _LOGGER.error("Error fetching data: %s", ex)
