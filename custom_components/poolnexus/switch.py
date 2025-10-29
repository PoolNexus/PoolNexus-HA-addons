"""Switch platform for PoolNexus integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.mqtt import async_publish
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
    serial = config.get(CONF_SERIAL) or config_entry.entry_id
    topic_prefix = f"{topic_prefix}/{serial}"
    
    # Créer tous les switches
    switches = []
    
    # Switch électrovanne
    switches.append(PoolNexusSwitch(
        hass, config_entry, topic_prefix, "electrovalve"
    ))
    
    # Switch remplissage automatique
    switches.append(PoolNexusSwitch(
        hass, config_entry, topic_prefix, "auto_fill"
    ))
    
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
