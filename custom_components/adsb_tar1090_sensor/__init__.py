"""The ADS-B tar1090 Sensor integration."""
from __future__ import annotations
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import (
    HomeAssistant
)
from .const import DOMAIN
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ADS-B tar1090 Sensor from a config entry.

    Args:
        hass (HomeAssistant): The Home Assistant instance.
        entry (ConfigEntry): The config entry representing the ADS-B tar1090 Sensor configuration.

    Returns:
        bool: _description_
    """
    _LOGGER.debug("ADS-B tar1090 Sensor Config data %s", str(entry))
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True
