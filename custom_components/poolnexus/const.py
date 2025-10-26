"""Constants for the PoolNexus integration."""

DOMAIN = "poolnexus"

# Configuration
CONF_MQTT_BROKER = "mqtt_broker"
CONF_MQTT_PORT = "mqtt_port"
CONF_MQTT_USERNAME = "mqtt_username"
CONF_MQTT_PASSWORD = "mqtt_password"
CONF_MQTT_TOPIC_PREFIX = "mqtt_topic_prefix"

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
    }
}

