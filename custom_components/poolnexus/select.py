"""Select platform for PoolNexus integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.mqtt import async_publish, async_subscribe
from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_MQTT_TOPIC_PREFIX,
    CONF_SERIAL,
    DOMAIN,
    SELECT_TYPES,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up PoolNexus select entities from a config entry."""
    config = config_entry.data
    topic_prefix = config.get(CONF_MQTT_TOPIC_PREFIX, "poolnexus")
    serial = config.get(CONF_SERIAL)
    if not serial:
        _LOGGER.error(
            "PoolNexus config entry %s missing 'serial' — skipping select setup",
            config_entry.entry_id,
        )
        return

    topic_prefix = f"{topic_prefix}/{serial}"

    selects = []
    for sel_key, sel_cfg in SELECT_TYPES.items():
        selects.append(PoolNexusSelect(hass, config_entry, topic_prefix, sel_key, sel_cfg))

    async_add_entities(selects)


class PoolNexusSelect(SelectEntity):
    """Representation of a PoolNexus selectable option."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        topic_prefix: str,
        select_type: str,
        select_cfg: dict[str, Any],
    ) -> None:
        self._hass = hass
        self._config_entry = config_entry
        self._topic_prefix = topic_prefix
        self._select_type = select_type
        self._select_cfg = select_cfg

        self._attr_name = f"PoolNexus {select_cfg.get('name', select_type)}"
        self._attr_unique_id = f"{config_entry.entry_id}_{select_type}"
        self._attr_options = list(select_cfg.get("options", []))
        self._attr_current_option = None
        self._unsubs: list = []

        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": "PoolNexus",
            "manufacturer": "PoolNexus",
            "model": "PoolNexus Device",
        }

    async def async_added_to_hass(self) -> None:
        state_topic = f"{self._topic_prefix}/{self._select_type}"
        set_topic = f"{state_topic}/set"

        @callback
        def _message_received(msg):
            try:
                payload = msg.payload.decode("utf-8").strip()
                if payload in self._attr_options:
                    self._attr_current_option = payload
                    self.async_write_ha_state()
                    _LOGGER.debug("Select %s updated to %s", self._select_type, payload)
            except Exception:
                _LOGGER.exception("Failed to parse select message for %s", state_topic)

        try:
            unsub1 = await async_subscribe(self._hass, state_topic, _message_received)
            if callable(unsub1):
                self._unsubs.append(unsub1)
        except Exception:
            _LOGGER.debug("No retained state topic %s for %s", state_topic, self.entity_id)

        try:
            unsub2 = await async_subscribe(self._hass, set_topic, _message_received)
            if callable(unsub2):
                self._unsubs.append(unsub2)
        except Exception:
            _LOGGER.debug("No retained set topic %s for %s", set_topic, self.entity_id)

    async def async_will_remove_from_hass(self) -> None:
        for unsub in list(self._unsubs):
            try:
                if callable(unsub):
                    unsub()
            except Exception:
                _LOGGER.debug("Unsubscribe failed for %s", self.entity_id)

    @property
    def current_option(self) -> str | None:
        return self._attr_current_option

    async def async_select_option(self, option: str) -> None:
        """Select an option and publish it to the device."""
        if option not in self._attr_options:
            _LOGGER.error("Invalid option for %s: %s", self._select_type, option)
            return

        topic = f"{self._topic_prefix}/{self._select_type}/set"
        await async_publish(self._hass, topic, option, retain=True)
        self._attr_current_option = option
        self.async_write_ha_state()
        _LOGGER.debug("Published select %s -> %s", self._select_type, option)
