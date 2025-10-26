"""Constants for the PoolNexus integration."""

DOMAIN = "poolnexus"

# Configuration
CONF_MQTT_BROKER = "mqtt_broker"
CONF_MQTT_PORT = "mqtt_port"
CONF_MQTT_USERNAME = "mqtt_username"
CONF_MQTT_PASSWORD = "mqtt_password"
CONF_MQTT_TOPIC_PREFIX = "mqtt_topic_prefix"

# Set values configuration
CONF_SET_PH_VALUE = "set_ph_value"
CONF_SET_REDOX_VALUE = "set_redox_value"
CONF_SET_TEMPERATURE_VALUE = "set_temperature_value"

# Default values
DEFAULT_MQTT_PORT = 1883
DEFAULT_MQTT_TOPIC_PREFIX = "poolnexus"

# Sensor types
SENSOR_TYPES = {
    "temperature": {
        "name": "Temperature",
        "unit_of_measurement": "°C",
        "device_class": "temperature",
        "state_class": "measurement",
    },
    "ph": {
        "name": "pH",
        "unit_of_measurement": "pH",
        "device_class": None,
        "state_class": "measurement",
    },
    "chlorine": {
        "name": "Chlore",
        "unit_of_measurement": "mg/L",
        "device_class": None,
        "state_class": "measurement",
    },
    "water_level": {
        "name": "Niveau d'eau",
        "unit_of_measurement": None,
        "device_class": None,
        "state_class": None,
    },
    "chlorine_level": {
        "name": "Niveau de chlore",
        "unit_of_measurement": None,
        "device_class": None,
        "state_class": None,
    },
    "ph_level": {
        "name": "Niveau de pH",
        "unit_of_measurement": None,
        "device_class": None,
        "state_class": None,
    },
}

# Switch types
SWITCH_TYPES = {
    "electrovalve": {
        "name": "Électrovanne",
        "icon": "mdi:valve",
    },
    "auto_fill": {
        "name": "Remplissage automatique",
        "icon": "mdi:water-plus",
    },
}

# Number types for set values
NUMBER_TYPES = {
    "set_ph": {
        "name": "Valeur pH cible",
        "unit_of_measurement": "pH",
        "min_value": 6.0,
        "max_value": 8.5,
        "step": 0.1,
        "icon": "mdi:ph",
    },
    "set_redox": {
        "name": "Valeur Redox cible",
        "unit_of_measurement": "mV",
        "min_value": 200,
        "max_value": 800,
        "step": 10,
        "icon": "mdi:flash",
    },
    "set_temperature": {
        "name": "Température cible",
        "unit_of_measurement": "°C",
        "min_value": 15,
        "max_value": 35,
        "step": 0.5,
        "icon": "mdi:thermometer",
    },
}

