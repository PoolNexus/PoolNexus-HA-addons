"""Text platform for PoolNexus integration."""
from __future__ import annotations

import logging
from typing import Any
import re

from homeassistant.components.mqtt import async_publish, async_subscribe
from homeassistant.components.text import TextEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_MQTT_TOPIC_PREFIX,
    CONF_SERIAL,
    DOMAIN,
    TEXT_TYPES,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up PoolNexus text entities from a config entry."""
    config = config_entry.data
    topic_prefix = config.get(CONF_MQTT_TOPIC_PREFIX, "poolnexus")
    # Require serial to build topics as <prefix>/<serial>/...
    serial = config.get(CONF_SERIAL)
    if not serial:
        _LOGGER.error(
            "PoolNexus config entry %s missing 'serial' — topics must use the format <prefix>/<serial>/...; skipping text entities setup",
            config_entry.entry_id,
        )
        return
    topic_prefix = f"{topic_prefix}/{serial}"
    
    # Créer tous les text entities
    text_entities = []
    
    # Text pour valeur pH cible
    text_entities.append(PoolNexusText(
        hass, config_entry, topic_prefix, "set_ph"
    ))
    
    # Text pour valeur Redox cible
    text_entities.append(PoolNexusText(
        hass, config_entry, topic_prefix, "set_redox"
    ))
    
    # Text pour température cible
    text_entities.append(PoolNexusText(
        hass, config_entry, topic_prefix, "set_temperature"
    ))
    
    async_add_entities(text_entities)


class PoolNexusText(TextEntity):
    """Representation of a PoolNexus text entity."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry, topic_prefix: str, text_type: str) -> None:
        """Initialize the text entity."""
        self._hass = hass
        self._config_entry = config_entry
        self._topic_prefix = topic_prefix
        self._text_type = text_type
        
        text_config = TEXT_TYPES[text_type]
        
        self._attr_name = f"PoolNexus {text_config['name']}"
        self._attr_unique_id = f"{config_entry.entry_id}_{text_type}"
        self._attr_icon = text_config.get("icon")
        self._attr_native_min = text_config.get("min_length")
        self._attr_native_max = text_config.get("max_length")
        self._attr_pattern = text_config.get("pattern")
        self._attr_native_value = ""

        # MQTT unsubscription handles (set when subscribed)
        self._unsubs = []

        # Configuration du device
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": "PoolNexus",
            "manufacturer": "NExus System",
            "model": "PoolNexus Device",
        }

    async def async_set_value(self, value: str) -> None:
        """Set the value."""
        # Validation du format selon le type
        if not self._validate_format(value):
            _LOGGER.error("Format invalide pour %s: %s", self._text_type, value)
            return
            
        await self._publish_value(value)

    async def async_added_to_hass(self) -> None:
        """Subscribe to the state topic for this text entity when added to hass.

        This allows values set on the device to be reflected in Home Assistant.
        The device is expected to publish the current value on
        `{prefix}/{serial}/{text_type}` (without `/set`). Retained messages
        will be delivered immediately when subscribing.
        """
        state_topic = f"{self._topic_prefix}/{self._text_type}"
        set_topic = f"{self._topic_prefix}/{self._text_type}/set"

        @callback
        def _message_received(msg):
            try:
                payload = msg.payload.decode("utf-8").strip()
                # Update local state with the device-published value
                self._attr_native_value = payload
                self.async_write_ha_state()
                _LOGGER.debug("Received %s state: %s", self._text_type, payload)
            except Exception:
                _LOGGER.exception("Failed to parse MQTT message for %s", state_topic)

        # Subscribe to both the state topic and the set topic to support
        # devices that publish retained values on either path.
        try:
            unsub_state = await async_subscribe(self._hass, state_topic, _message_received)
            if callable(unsub_state):
                self._unsubs.append(unsub_state)
        except Exception:
            _LOGGER.exception("Failed to subscribe to %s for %s", state_topic, self.entity_id)

        try:
            unsub_set = await async_subscribe(self._hass, set_topic, _message_received)
            if callable(unsub_set):
                self._unsubs.append(unsub_set)
        except Exception:
            _LOGGER.debug("No retained/set topic available for %s (topic: %s)", self.entity_id, set_topic)

    async def async_will_remove_from_hass(self) -> None:
        """Cleanup subscription when entity is removed."""
        for unsub in list(self._unsubs):
            try:
                if callable(unsub):
                    unsub()
            except Exception:
                _LOGGER.debug("Unsubscribe failed for %s", self.entity_id)

    def _validate_format(self, value: str) -> bool:
        """Validate the format of the input value."""
        if self._text_type == "set_ph":
            # Format: XX.X (ex: 07.2)
            return bool(re.match(r"^\d{2}\.\d$", value))
        elif self._text_type == "set_redox":
            # Format: X.XXX (ex: 6.500)
            return bool(re.match(r"^\d\.\d{3}$", value))
        elif self._text_type == "set_temperature":
            # Format: XX.X (ex: 25.0)
            return bool(re.match(r"^\d{2}\.\d$", value))
        return True

    async def _publish_value(self, value: str) -> None:
        """Publish the value to MQTT."""
        topic = f"{self._topic_prefix}/{self._text_type}/set"
        payload = value
        
        await async_publish(
            self._hass,
            topic,
            payload,
            retain=True
        )
        
        self._attr_native_value = value
        self.async_write_ha_state()
        
        _LOGGER.debug("Published %s value: %s", self._text_type, payload)
