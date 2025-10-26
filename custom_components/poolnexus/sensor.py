"""Sensor platform for PoolNexus integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.mqtt import async_subscribe
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import (
    CONF_MQTT_TOPIC_PREFIX,
    DOMAIN,
    SENSOR_TYPES,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up PoolNexus sensors from a config entry."""
    config = config_entry.data
    topic_prefix = config.get(CONF_MQTT_TOPIC_PREFIX, "poolnexus")
    
    # Créer le capteur de température
    temperature_sensor = PoolNexusTemperatureSensor(
        hass, config_entry, topic_prefix
    )
    
    async_add_entities([temperature_sensor])


class PoolNexusTemperatureSensor(SensorEntity):
    """Representation of a PoolNexus temperature sensor."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry, topic_prefix: str) -> None:
        """Initialize the sensor."""
        self._hass = hass
        self._config_entry = config_entry
        self._topic_prefix = topic_prefix
        self._attr_name = "PoolNexus Temperature"
        self._attr_unique_id = f"{config_entry.entry_id}_temperature"
        self._attr_device_class = "temperature"
        self._attr_native_unit_of_measurement = "°C"
        self._attr_state_class = "measurement"
        self._attr_native_value = None
        
        # Configuration du device
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": "PoolNexus",
            "manufacturer": "PoolNexus",
            "model": "PoolNexus Device",
        }

    async def async_added_to_hass(self) -> None:
        """Subscribe to MQTT topic when entity is added to hass."""
        temperature_topic = f"{self._topic_prefix}/temperature"
        
        @callback
        def message_received(msg):
            """Handle new MQTT messages."""
            try:
                # Convertir la valeur en float
                value = float(msg.payload)
                self._attr_native_value = value
                self.async_write_ha_state()
                _LOGGER.debug("Received temperature: %s", value)
            except (ValueError, TypeError) as err:
                _LOGGER.error("Invalid temperature value: %s", msg.payload)
        
        # S'abonner au topic MQTT
        await async_subscribe(self._hass, temperature_topic, message_received)

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self._attr_native_value
