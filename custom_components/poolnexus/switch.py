"""Switch platform for PoolNexus integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.mqtt import async_publish, async_subscribe
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_MQTT_TOPIC_PREFIX,
    CONF_SERIAL,
    DOMAIN,
    SWITCH_TYPES,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up PoolNexus switches from a config entry."""
    config = config_entry.data
    topic_prefix = config.get(CONF_MQTT_TOPIC_PREFIX, "poolnexus")
    # Require serial to build topics as <prefix>/<serial>/...
    serial = config.get(CONF_SERIAL)
    if not serial:
        _LOGGER.error(
            "PoolNexus config entry %s missing 'serial' — topics must use the format <prefix>/<serial>/...; skipping switch setup",
            config_entry.entry_id,
        )
        return
    topic_prefix = f"{topic_prefix}/{serial}"
    
    # Créer tous les switches
    switches = []

    # Create a switch for each declared SWITCH_TYPES so README and code stay in sync
    for sw_type in SWITCH_TYPES:
        switches.append(PoolNexusSwitch(hass, config_entry, topic_prefix, sw_type))

    async_add_entities(switches)


class PoolNexusSwitch(SwitchEntity):
    """Representation of a PoolNexus switch."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry, topic_prefix: str, switch_type: str) -> None:
        """Initialize the switch."""
        self._hass = hass
        self._config_entry = config_entry
        self._topic_prefix = topic_prefix
        self._switch_type = switch_type
        
        switch_config = SWITCH_TYPES[switch_type]
        
        self._attr_name = f"PoolNexus {switch_config['name']}"
        self._attr_unique_id = f"{config_entry.entry_id}_{switch_type}"
        self._attr_icon = switch_config.get("icon")
        self._attr_is_on = False
        
        # Configuration du device
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": "PoolNexus",
            "manufacturer": "Nexus System",
            "model": "PoolNexus Device",
        }
        # keep unsubscribe callables for subscriptions created in async_added_to_hass
        self._unsubs: list = []

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        await self._publish_state(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        await self._publish_state(False)

    async def _publish_state(self, state: bool) -> None:
        """Publish the switch state to MQTT."""
        topic = f"{self._topic_prefix}/{self._switch_type}/set"
        payload = "ON" if state else "OFF"
        
        await async_publish(
            self._hass,
            topic,
            payload,
            retain=True
        )
        
        self._attr_is_on = state
        self.async_write_ha_state()
        
        _LOGGER.debug("Published %s state: %s", self._switch_type, payload)

    async def async_added_to_hass(self) -> None:
        """Subscribe to state topics when entity is added so device-published state is reflected in HA."""
        state_topic = f"{self._topic_prefix}/{self._switch_type}"
        state_topic_state = f"{state_topic}/state"

        @callback
        def _message_received(msg):
            try:
                payload = msg.payload.decode("utf-8").strip()
                is_on = self._parse_payload_to_bool(payload)
                self._attr_is_on = is_on
                self.async_write_ha_state()
                _LOGGER.debug("Received %s state: %s", self._switch_type, payload)
            except Exception:
                _LOGGER.exception("Failed to parse switch state for %s", self._switch_type)

        # subscribe to both possible state topics to capture retained messages
        try:
            unsub1 = await async_subscribe(self._hass, state_topic_state, _message_received)
            if callable(unsub1):
                self._unsubs.append(unsub1)
        except Exception:
            _LOGGER.debug("No state topic %s for %s", state_topic_state, self.entity_id)

        try:
            unsub2 = await async_subscribe(self._hass, state_topic, _message_received)
            if callable(unsub2):
                self._unsubs.append(unsub2)
        except Exception:
            _LOGGER.debug("No state topic %s for %s", state_topic, self.entity_id)

    async def async_will_remove_from_hass(self) -> None:
        """Cleanup MQTT subscriptions on removal."""
        for unsub in list(self._unsubs):
            try:
                if callable(unsub):
                    unsub()
            except Exception:
                _LOGGER.debug("Unsubscribe failed for %s", self.entity_id)

    def _parse_payload_to_bool(self, payload: str) -> bool:
        """Parse common payload formats to boolean state.

        Accepts: ON/OFF, true/false, 1/0, locked/unlocked
        """
        if payload is None:
            return False
        p = str(payload).strip().lower()
        if p in ("on", "true", "1", "locked"):
            return True
        if p in ("off", "false", "0", "unlocked"):
            return False
        # try numeric
        try:
            return float(p) != 0
        except Exception:
            return False
