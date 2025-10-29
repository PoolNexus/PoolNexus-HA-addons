from __future__ import annotations

import asyncio
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv
from homeassistant.components.mqtt import async_subscribe

from .const import (
    CONF_MQTT_BROKER,
    CONF_MQTT_PASSWORD,
    CONF_MQTT_PORT,
    CONF_MQTT_TOPIC_PREFIX,
    CONF_MQTT_USERNAME,
    CONF_SERIAL,
    DEFAULT_MQTT_PORT,
    DEFAULT_MQTT_TOPIC_PREFIX,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_MQTT_BROKER): str,
        vol.Optional(CONF_MQTT_PORT, default=DEFAULT_MQTT_PORT): cv.port,
        vol.Optional(CONF_MQTT_USERNAME): str,
        vol.Optional(CONF_MQTT_PASSWORD): str,
        vol.Optional(CONF_MQTT_TOPIC_PREFIX, default=DEFAULT_MQTT_TOPIC_PREFIX): str,
        vol.Optional("scan_devices", default=False): bool,
        vol.Optional(CONF_SERIAL): str,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for PoolNexus."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        self._temp_user_input = user_input

        if user_input.get("scan_devices"):
            prefix = user_input.get(CONF_MQTT_TOPIC_PREFIX, DEFAULT_MQTT_TOPIC_PREFIX)
            found = await self._scan_for_serials(self.hass, prefix)
            if not found:
                # No devices detected — fall back to creating the entry
                # with the provided data (user can manually enter serial).
                unique = user_input.get(CONF_SERIAL) or user_input.get(CONF_MQTT_BROKER)
                if unique:
                    await self.async_set_unique_id(str(unique))
                    self._abort_if_unique_id_configured()
                return self.async_create_entry(title="PoolNexus", data=user_input)

            # Show a form to let the user pick one of the discovered serials
            return self.async_show_form(
                step_id="select_serial",
                data_schema=vol.Schema({vol.Required(CONF_SERIAL): vol.In(found)}),
            )

        # No scan requested — require a serial to be provided. The integration
        # expects topics in the exact format <prefix>/<serial>/..., so we need
        # the serial number at configuration time.
        if not user_input.get(CONF_SERIAL):
            # Ask the user to provide the device serial
            return self.async_show_form(
                step_id="require_serial",
                data_schema=vol.Schema({vol.Required(CONF_SERIAL): str}),
            )

        unique = user_input.get(CONF_SERIAL)
        if unique:
            await self.async_set_unique_id(str(unique))
            self._abort_if_unique_id_configured()

        return self.async_create_entry(title="PoolNexus", data=user_input)

    async def async_step_require_serial(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Request serial if it was not provided initially."""
        if user_input is None:
            return self.async_show_form(
                step_id="require_serial",
                data_schema=vol.Schema({vol.Required(CONF_SERIAL): str}),
            )

        data = dict(self._temp_user_input or {})
        data[CONF_SERIAL] = user_input[CONF_SERIAL]

        unique = data.get(CONF_SERIAL)
        if unique:
            await self.async_set_unique_id(str(unique))
            self._abort_if_unique_id_configured()

        return self.async_create_entry(title="PoolNexus", data=data)

    async def async_step_select_serial(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle selection of a detected serial from a previous scan."""
        # The initial data is stored in self._temp_user_input
        if user_input is None:
            return self.async_abort(reason="no_selection")

        data = dict(self._temp_user_input or {})
        data[CONF_SERIAL] = user_input[CONF_SERIAL]

        unique = data.get(CONF_SERIAL) or data.get(CONF_MQTT_BROKER)
        if unique:
            await self.async_set_unique_id(str(unique))
            self._abort_if_unique_id_configured()

        return self.async_create_entry(title="PoolNexus", data=data)

    async def _scan_for_serials(self, hass: HomeAssistant, prefix: str, timeout: float = 2.0) -> list[str]:
        """Subscribe briefly to MQTT under `prefix/#` and collect serial segments.

        We assume the device publishes topics like <prefix>/<serial>/...; this
        function returns the set of first path segments after the prefix that
        were observed (keeps order deterministic by sorting).
        """
        found: set[str] = set()

        topic = f"{prefix}/#"

        @callback
        def _message(msg):
            try:
                t = msg.topic
                # strip prefix + '/'
                if not t.startswith(f"{prefix}/"):
                    return
                rem = t[len(prefix) + 1 :]
                parts = rem.split("/")
                if parts:
                    found.add(parts[0])
            except Exception:
                return

        # Subscribe and wait for a short period to receive retained messages.
        unsub = await async_subscribe(hass, topic, _message)
        try:
            await asyncio.sleep(timeout)
        finally:
            try:
                unsub()
            except Exception:
                # some mqtt helpers return coroutines or cleanup differently;
                # ignore unsubscription errors.
                pass

        return sorted(found)
