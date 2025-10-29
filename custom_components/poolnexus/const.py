"""Constants for the PoolNexus integration."""

DOMAIN = "poolnexus"

# Configuration
CONF_MQTT_BROKER = "mqtt_broker"
CONF_MQTT_PORT = "mqtt_port"
CONF_MQTT_USERNAME = "mqtt_username"
CONF_MQTT_PASSWORD = "mqtt_password"
CONF_MQTT_TOPIC_PREFIX = "mqtt_topic_prefix"
CONF_SERIAL = "serial"

# Set values configuration
CONF_SET_PH_VALUE = "set_ph_value"
CONF_SET_REDOX_VALUE = "set_redox_value"
CONF_SET_TEMPERATURE_VALUE = "set_temperature_value"

# Default values
DEFAULT_MQTT_PORT = 1883
DEFAULT_MQTT_TOPIC_PREFIX = "poolnexus"
DEFAULT_SERIAL = None

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
        "unit_of_measurement": "mV",
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
    # Informational / text sensors
    "firmware": {
        "name": "Firmware",
        "unit_of_measurement": None,
        "device_class": None,
        "state_class": None,
    },
    "last_pH_prob_cal": {
        "name": "Dernière calibration pH",
        "unit_of_measurement": None,
        "device_class": None,
        "state_class": None,
    },
    "last_ORP_prob_cal": {
        "name": "Dernière calibration ORP",
        "unit_of_measurement": None,
        "device_class": None,
        "state_class": None,
    },
    "availability": {
        "name": "Disponibilité",
        "unit_of_measurement": None,
        "device_class": None,
        "state_class": None,
    },
    "alert": {
        "name": "Alert",
        "unit_of_measurement": None,
        "device_class": None,
        "state_class": None,
    },
    "last_pump_cleaning": {
        "name": "Dernier nettoyage pompe",
        "unit_of_measurement": None,
        "device_class": None,
        "state_class": None,
    },
    "operating_mode": {
        "name": "Mode de fonctionnement",
        "unit_of_measurement": None,
        "device_class": None,
        "state_class": None,
    },
    "screen_lock": {
        "name": "Verrouillage écran",
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
    "pump": {
        "name": "Pompe de circulation",
        "icon": "mdi:fan",
    },
    "switch_1": {
        "name": "Switch 1",
        "icon": "mdi:toggle-switch",
    },
    "switch_2": {
        "name": "Switch 2",
        "icon": "mdi:toggle-switch-off",
    },
}

# Text types for set values
TEXT_TYPES = {
    "set_ph": {
        "name": "Valeur pH cible",
        "min_length": 1,
        "max_length": 4,
        "pattern": r"^\d+\.\d$",
        "icon": "mdi:ph",
    },
    "set_redox": {
        "name": "Valeur Redox cible",
        "min_length": 1,
        "max_length": 5,
        "pattern": r"^\d+\.\d{3}$",
        "icon": "mdi:flash",
    },
    "set_temperature": {
        "name": "Température cible",
        "min_length": 1,
        "max_length": 4,
        "pattern": r"^\d+\.\d$",
        "icon": "mdi:thermometer",
    },
}

