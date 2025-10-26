"""Number platform for PoolNexus integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.mqtt import async_publish
from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_MQTT_TOPIC_PREFIX,
    DOMAIN,
    NUMBER_TYPES,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up PoolNexus numbers from a config entry."""
    config = config_entry.data
    topic_prefix = config.get(CONF_MQTT_TOPIC_PREFIX, "poolnexus")
    
    # Créer tous les numbers
    numbers = []
    
    # Number pour valeur pH cible
    numbers.append(PoolNexusNumber(
        hass, config_entry, topic_prefix, "set_ph"
    ))
    
    # Number pour valeur Redox cible
    numbers.append(PoolNexusNumber(
        hass, config_entry, topic_prefix, "set_redox"
    ))
    
    # Number pour température cible
    numbers.append(PoolNexusNumber(
        hass, config_entry, topic_prefix, "set_temperature"
    ))
    
    async_add_entities(numbers)


class PoolNexusNumber(NumberEntity):
    """Representation of a PoolNexus number."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry, topic_prefix: str, number_type: str) -> None:
        """Initialize the number."""
        self._hass = hass
        self._config_entry = config_entry
        self._topic_prefix = topic_prefix
        self._number_type = number_type
        
        number_config = NUMBER_TYPES[number_type]
        
        self._attr_name = f"PoolNexus {number_config['name']}"
        self._attr_unique_id = f"{config_entry.entry_id}_{number_type}"
        self._attr_icon = number_config.get("icon")
        self._attr_native_unit_of_measurement = number_config.get("unit_of_measurement")
        self._attr_native_min_value = number_config.get("min_value")
        self._attr_native_max_value = number_config.get("max_value")
        self._attr_native_step = number_config.get("step")
        self._attr_native_value = None
        
        # Configuration du device
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": "PoolNexus",
            "manufacturer": "PoolNexus",
            "model": "PoolNexus Device",
        }

    async def async_set_native_value(self, value: float) -> None:
        """Set the value."""
        await self._publish_value(value)

    async def _publish_value(self, value: float) -> None:
        """Publish the value to MQTT."""
        topic = f"{self._topic_prefix}/{self._number_type}/set"
        payload = str(value)
        
        await async_publish(
            self._hass,
            topic,
            payload,
            retain=True
        )
        
        self._attr_native_value = value
        self.async_write_ha_state()
        
        _LOGGER.debug("Published %s value: %s", self._number_type, payload)
