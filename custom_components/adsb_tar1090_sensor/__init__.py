"""The ADS-B tar1090 Sensor integration."""
from __future__ import annotations
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import (
    HomeAssistant
)
from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up OpenAI Service from a config entry."""

    hass.data.setdefault(DOMAIN, {})
    _LOGGER.debug("ADS-B tar1090 Sensor Config data %s", str(entry))

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True
