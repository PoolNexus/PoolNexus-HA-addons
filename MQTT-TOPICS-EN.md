# MQTT — Topics used by the PoolNexus integration

This document lists the MQTT topics used by the PoolNexus integration (source files: `sensor.py`, `switch.py`, `text.py`, `config_flow.py`). Topics now use the required format `{prefix}/{serialNumber}/...` — the device serial (`serial`) must be provided during configuration.

## Prefix and segmentation
- Configuration key (config flow / entry data): `mqtt_topic_prefix`
- Default value: `poolnexus`
-- Required device identifier key: `serial` (string). The integration requires this field to build topics.

General topic format
- <mqtt_topic_prefix>/<serialNumber>/<resource>

Examples (with `mqtt_topic_prefix = poolnexus` and `serial = SN12345`):

### Sensors
Sensors subscribe to:
- `poolnexus/SN12345/temperature` — temperature (parsed as float)
- `poolnexus/SN12345/ph` — pH (float)
- `poolnexus/SN12345/chlorine` — chlorine (float)
- `poolnexus/SN12345/water_level` — water level (textual values: e.g. `on`/`off` or labels)
- `poolnexus/SN12345/chlorine_level` — chlorine level state (text)
- `poolnexus/SN12345/ph_level` — pH level state (text)

Note: The code expects numeric payloads for numeric sensors (floats) and textual payloads for some state sensors.

## Information topics (read-only)
In addition to sensors and commands, the integration also listens to several information topics:
- `poolnexus/SN12345/firmware` — firmware version (e.g. `1.2.3`)
- `poolnexus/SN12345/last_pH_prob_cal` — last pH probe calibration timestamp (e.g. `12/06/24 14:30`)
- `poolnexus/SN12345/last_ORP_prob_cal` — last ORP probe calibration timestamp (e.g. `12/06/24 14:30`)
- `poolnexus/SN12345/availability` — availability (`online` / `offline`)
- `poolnexus/SN12345/alert` — alert messages as JSON (e.g. `{"type":"ph_high","message":"pH too high"}`)

## Other information & state
Some additional topics the device may publish:
- `poolnexus/SN12345/last_pump_cleaning` — last pump cleaning timestamp (e.g. `12/06/24 10:00`)
- `poolnexus/SN12345/operating_mode` — operating mode (expected values: `hybernation_passive`, `hybernation_active`, `normal`)
- `poolnexus/SN12345/screen_lock` — screen lock state (expected values: `locked` / `unlocked` or `true` / `false`)

### Switches
Switches publish to `.../<switch_type>/set` topics:
- `poolnexus/SN12345/electrovalve/set` — payload `ON` / `OFF` (published with `retain=True`)
- `poolnexus/SN12345/auto_fill/set` — payload `ON` / `OFF` (published with `retain=True`)
 - `poolnexus/SN12345/pump/set` — payload `ON` / `OFF` (published with `retain=True`)
 - `poolnexus/SN12345/switch_1/set` — payload `ON` / `OFF` (published with `retain=True`)
 - `poolnexus/SN12345/switch_2/set` — payload `ON` / `OFF` (published with `retain=True`)

Switches use `homeassistant.components.mqtt.async_publish(..., retain=True)`.

### Text entities (configurable setpoints)
Text entities publish to `.../<text_type>/set` topics:
- `poolnexus/SN12345/set_ph/set` — expected format `\d{2}\.\d` (e.g. `07.2`), `retain=True`
- `poolnexus/SN12345/set_redox/set` — expected format `\d\.\d{3}` (e.g. `6.500`), `retain=True`
- `poolnexus/SN12345/set_temperature/set` — expected format `\d{2}\.\d` (e.g. `25.0`), `retain=True`

`TextEntity` validates the format before publishing and uses retained messages for broker persistence.

## Automatic detection (scan) used by the config flow
The config flow provides a `scan_devices` option that briefly subscribes to:
- `<prefix>/#` (for example `poolnexus/#`) and collects the first path segments observed after the prefix.

Detection heuristic:
- We assume devices publish under the pattern `prefix/<serial>/...` (for example `poolnexus/SN12345/temperature`).
- The scanner collects the first segments (`SN12345`) and offers them to the user for selection.
- The scan works best when devices publish retained messages (retained messages are delivered immediately to a new subscriber).

If your devices do not use this announcement pattern, provide the exact announcement topic (e.g. `poolnexus/announce/<serial>` or `poolnexus/<serial>/info`) so the scanner can be adapted.

## Operational notes
- Switches and text entities publish with `retain=True`. If you change the topic structure (for example during migration), remember to clean or republish retained messages on the new paths.
 - To avoid collisions on a shared broker, provide `serial` at config time (required). The integration no longer uses an `entry_id` fallback.

## Where the logic lives in the code
- `custom_components/poolnexus/sensor.py` — topic construction and subscription (`async_subscribe`).
- `custom_components/poolnexus/switch.py` — topic construction and publishing (`async_publish` with `retain=True`).
- `custom_components/poolnexus/text.py` — format validation and publishing (`async_publish` with `retain=True`).
- `custom_components/poolnexus/config_flow.py` — `scan_devices` option and `serial` handling.

---


---
Links:
- French version of this document: `MQTT-TOPICS.md`
- README (EN): `README-EN.md`
- README (FR): `README.md`

If you want, I can:
- Add concrete examples with real serial numbers.
- Add a migration checklist to copy retained messages from the old topic paths to the new ones (careful: destructive if done wrongly).
- Integrate this document into the main `README.md` or add a link to it.

Tell me which option you prefer and I will apply it.