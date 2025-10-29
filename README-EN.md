# PoolNexus HA Addons

Home Assistant integration for PoolNexus devices via MQTT.

IMPORTANT: MQTT topics are namespaced per device to avoid collisions when
multiple PoolNexus instances share the same broker. The topic format is:

```
<mqtt_topic_prefix>/<serial_or_entry_id>/<resource>
```

Where `serial` is optional (config flow field `serial`). If no `serial` is
provided, the integration falls back to `config_entry.entry_id` (a Home
Assistant UUID) to isolate topics.

See `MQTT-TOPICS-EN.md` for the complete topic list and examples.

Links:
- French README: `README.md`
- MQTT topics (FR): `MQTT-TOPICS.md`

## Installation

This integration can be installed via HACS (Home Assistant Community Store).

1. Add this repository to HACS
2. Install the integration
3. Restart Home Assistant
4. Add the integration via Configuration > Integrations

## Configuration

### UI configuration

1. Go to Configuration > Integrations
2. Click "Add integration"
3. Search for "PoolNexus"
4. Configure MQTT settings:
   - **MQTT Broker**: IP or hostname of the MQTT broker
   - **Port**: Broker port (default: 1883)
   - **Username**: MQTT username (optional)
   - **Password**: MQTT password (optional)
   - **Topic prefix**: MQTT topic prefix (default: poolnexus)
   - **Serial (optional)**: device serial to namespace topics as `poolnexus/<serial>/...`
   - **Scan devices (optional)**: briefly scan the broker for devices under the prefix

### Manual configuration

You can also add an entry via `configuration.yaml` (UI config is preferred):

```yaml
poolnexus:
  mqtt_broker: "192.168.1.100"
  mqtt_port: 1883
  mqtt_username: "mqtt_user"
  mqtt_password: "mqtt_password"
  mqtt_topic_prefix: "poolnexus"
```

## Where to find MQTT topics

See `MQTT-TOPICS-EN.md` for exact topic names, examples and migration notes.

## Support

For support and questions, please open an issue on the GitHub repository.
