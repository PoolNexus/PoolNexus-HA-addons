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
    
    # Créer tous les capteurs
    sensors = []
    
    # Capteur de température
    sensors.append(PoolNexusSensor(
        hass, config_entry, topic_prefix, "temperature"
    ))
    
    # Capteur de pH
    sensors.append(PoolNexusSensor(
        hass, config_entry, topic_prefix, "ph"
    ))
    
    # Capteur de chlore
    sensors.append(PoolNexusSensor(
        hass, config_entry, topic_prefix, "chlorine"
    ))
    
    # Capteur de niveau d'eau (on/off)
    sensors.append(PoolNexusSensor(
        hass, config_entry, topic_prefix, "water_level"
    ))
    
    # Capteur de niveau de chlore (low/no liquid/ok)
    sensors.append(PoolNexusSensor(
        hass, config_entry, topic_prefix, "chlorine_level"
    ))
    
    # Capteur de niveau de pH (low/no liquid/ok)
    sensors.append(PoolNexusSensor(
        hass, config_entry, topic_prefix, "ph_level"
    ))
    
    async_add_entities(sensors)


class PoolNexusSensor(SensorEntity):
    """Representation of a PoolNexus sensor."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry, topic_prefix: str, sensor_type: str) -> None:
        """Initialize the sensor."""
        self._hass = hass
        self._config_entry = config_entry
        self._topic_prefix = topic_prefix
        self._sensor_type = sensor_type
        
        sensor_config = SENSOR_TYPES[sensor_type]
        
        self._attr_name = f"PoolNexus {sensor_config['name']}"
        self._attr_unique_id = f"{config_entry.entry_id}_{sensor_type}"
        self._attr_device_class = sensor_config.get("device_class")
        self._attr_native_unit_of_measurement = sensor_config.get("unit_of_measurement")
        self._attr_state_class = sensor_config.get("state_class")
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
        topic = f"{self._topic_prefix}/{self._sensor_type}"
        
        @callback
        def message_received(msg):
            """Handle new MQTT messages."""
            try:
                payload = msg.payload.decode("utf-8").strip()
                
                # Gestion spéciale pour les capteurs de niveau avec valeurs textuelles
                if self._sensor_type in ["water_level", "chlorine_level", "ph_level"]:
                    self._attr_native_value = payload
                else:
                    # Conversion en float pour les valeurs numériques
                    value = float(payload)
                    self._attr_native_value = value
                
                self.async_write_ha_state()
                _LOGGER.debug("Received %s: %s", self._sensor_type, payload)
            except (ValueError, TypeError) as err:
                _LOGGER.error("Invalid %s value: %s", self._sensor_type, msg.payload)
        
        # S'abonner au topic MQTT
        await async_subscribe(self._hass, topic, message_received)

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self._attr_native_value
