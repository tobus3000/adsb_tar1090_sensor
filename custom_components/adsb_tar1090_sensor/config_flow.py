"""Config flow for the ADS-B rtl1090 Sensor."""
from __future__ import annotations
import logging
from typing import Any
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME, CONF_URL
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv
from .connection_hub import (
    ConnectionHub,
    CannotConnect
)
from .const import (
    CONF_URL,
    CONF_UPDATE_INTERVAL,
    CONF_DISTANCE_THRESHOLD,
    CONF_EMERGENCY_SQUAWK,
    CONF_SPECIAL_SQUAWK,
    DEFAULT_NAME,
    DEFAULT_UPDATE_INTERVAL_SECONDS,
    DEFAULT_DISTANCE_THRESHOLD_KM,
    DEFAULT_URL,
    DEFAULT_EMERGENCY_SQUAWK,
    DEFAULT_SPECIAL_SQUAWK,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

ADSB_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Required(CONF_URL, default=DEFAULT_URL): cv.string
    }
)

async def validate_input(data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user URL input."""
    hub = ConnectionHub(endpoint_url=data.get("url"))
    if not await hub.test_connect():
        raise CannotConnect
    # Return info that you want to store in the config entry.
    return {}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ADS-B rtl1090 Sensor."""

    VERSION = 1
    MINOR_VERSION = 0

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                user_input.update(info)
                return self.async_create_entry(
                    title=user_input["name"], data=user_input
                )

        return self.async_show_form(
            step_id="user", data_schema=ADSB_SCHEMA, errors=errors
        )


    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handles options flow for the component."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize the Option Flow handler."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options of the ADS-B rtl1090 Sensor."""

        # Retrieve the options associated with the config entry
        options = self.config_entry.options or {}
        if user_input is not None:
            # Value of data will be set on the options property of our config_entry
            # instance.
            _LOGGER.debug("Saving ADS-B rtl1090 Sensor options: %s", user_input)
            return self.async_create_entry(
                title="ADS-B rtl1090 Sensor Options Updated",
                data=user_input,
            )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_UPDATE_INTERVAL,
                        default=options.get(
                            "upate_interval",
                            DEFAULT_UPDATE_INTERVAL_SECONDS
                        )
                    ): cv.positive_int,
                    vol.Optional(
                        CONF_DISTANCE_THRESHOLD,
                        default=options.get(
                            "distance_threshold",
                            DEFAULT_DISTANCE_THRESHOLD_KM
                        ),
                    ): cv.positive_float,
                    vol.Optional(
                        CONF_EMERGENCY_SQUAWK,
                        default=options.get(
                            "emergency_squawk",
                            DEFAULT_EMERGENCY_SQUAWK
                        ),
                    ): cv.ensure_list,
                    vol.Optional(
                        CONF_SPECIAL_SQUAWK,
                        default=options.get(
                            "special_squawk",
                            DEFAULT_SPECIAL_SQUAWK
                        ),
                    ): cv.ensure_list,

                }
            ),
        )
