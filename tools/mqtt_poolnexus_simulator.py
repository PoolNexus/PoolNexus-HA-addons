"""
Simple MQTT simulator for PoolNexus devices.

This script connects to an MQTT broker, publishes periodic simulated sensor
values under the topic `<prefix>/<serial>/<sensor>` and publishes retained
state messages. It subscribes to `<prefix>/<serial>/*/set` topics so it can
apply changes coming from Home Assistant and then publishes the resulting
state back (retained) so HA sees the new/current value.

Usage (PowerShell):
    # Pass username/password on the command line (visible in history):
    python tools/mqtt_poolnexus_simulator.py --host 127.0.0.1 --port 1883 --prefix poolnexus --serial SIM12345 --username myuser --password mypass

    # Or set environment variables (safer):
    $env:MQTT_USERNAME='myuser'; $env:MQTT_PASSWORD='mypassword'; \
      python tools/mqtt_poolnexus_simulator.py --host 127.0.0.1 --prefix poolnexus --serial SIM12345

    # Or provide only --username and you will be prompted for the password (recommended):
    python tools/mqtt_poolnexus_simulator.py --host 127.0.0.1 --prefix poolnexus --serial SIM12345 --username myuser

Dependencies:
    pip install paho-mqtt

Notes:
 - The simulator publishes telemetry every `--interval` seconds.
 - It publishes initial retained states on connect.
 - It listens to command topics for text, switches and select (operating_mode).
"""

import argparse
import getpass
import inspect
import json
import logging
import os
import random
import threading
import time
import warnings
from typing import Any, Dict

import paho.mqtt.client as mqtt

_LOGGER = logging.getLogger("poolnexus_simulator")

DEFAULT_PREFIX = "poolnexus"

# Default simulated values
DEFAULT_STATE = {
    "temperature": 25.0,
    "ph": 7.2,
    # chlorine in mV or normalized value; examples use a small decimal -> use float with 3 decimals
    "chlorine": 0.802,
    # textual status values (lowercase per README)
    "water_level": "nok",
    "chlorine_level": "ok",
    "ph_level": "low",
    # informational
    "firmware": "1.2.3",
    # date/time in DD/MM/YY HH:MM format
    "last_pH_prob_cal": "01/01/25 12:00",
    "last_ORP_prob_cal": "02/01/25 12:00",
    "availability": "online",
    "alert": "{\"type\": \"none\", \"message\": \"\", \"timestamp\": \"\"}",
    "last_pump_cleaning": "01/05/25 12:00",
    # text/settable targets
    "set_ph": "07.2",
    "set_redox": "6.500",
    "set_temperature": "25.0",
    # switches
    "electrovalve": False,
    "auto_fill": False,
    "pump": True,
    "switch_1": False,
    "switch_2": False,
    "screen_lock": False,
    # select
    "operating_mode": "normal",
}

TEXT_TYPES = ["set_ph", "set_redox", "set_temperature"]
SWITCH_TYPES = ["electrovalve", "auto_fill", "pump", "switch_1", "switch_2", "screen_lock"]
SELECT_TYPES = ["operating_mode"]
SENSOR_TYPES = ["temperature", "ph", "chlorine", "water_level", "chlorine_level", "ph_level"]
INFO_TYPES = ["firmware", "last_pH_prob_cal", "last_ORP_prob_cal", "availability", "alert", "last_pump_cleaning"]


def topic(base: str, key: str) -> str:
    return f"{base}/{key}"


def command_topic(base: str, key: str) -> str:
    # controller -> device
    return f"{base}/{key}/set"


class PoolNexusSimulator:
    def __init__(self, client: mqtt.Client, prefix: str, serial: str, interval: float = 10.0):
        self.client = client
        self.prefix = prefix
        self.serial = serial
        self.base = f"{self.prefix}/{self.serial}"
        self.interval = interval
        self.running = False
        self.state: Dict[str, Any] = DEFAULT_STATE.copy()
        self.lock = threading.Lock()

    def publish_retained(self, key: str, value: Any):
        t = topic(self.base, key)
        payload = str(value)
        _LOGGER.debug("Publishing retained %s -> %s", t, payload)
        # publish the primary topic
        try:
            self.client.publish(t, payload, retain=True)
        except Exception:
            _LOGGER.exception("Failed to publish to %s", t)
        # Also publish a /state variant for compatibility (some firmware use <key>/state)
        state_t = f"{t}/state"
        try:
            self.client.publish(state_t, payload, retain=True)
        except Exception:
            _LOGGER.debug("Failed to publish state variant to %s", state_t)

    def publish_all_initial(self):
        # publish sensors, info, switches, texts, select
        with self.lock:
            for k in SENSOR_TYPES + INFO_TYPES:
                self.publish_retained(k, self.state.get(k, ""))
            for k in TEXT_TYPES + SWITCH_TYPES + SELECT_TYPES:
                # text/select/switch state topic
                self.publish_retained(k, self.state.get(k, ""))

    def handle_set_message(self, key: str, payload: str):
        _LOGGER.info("Set request %s = %s", key, payload)
        payload = payload.strip()
        with self.lock:
            if key in TEXT_TYPES:
                # accept any text but store as-is
                self.state[key] = payload
                # publish updated state (no /set suffix)
                self.publish_retained(key, self.state[key])
            elif key in SWITCH_TYPES:
                val = self._parse_bool(payload)
                self.state[key] = val
                self.publish_retained(key, "ON" if val else "OFF")
            elif key in SELECT_TYPES:
                # operating_mode -> store string
                self.state[key] = payload
                self.publish_retained(key, self.state[key])
            else:
                _LOGGER.warning("Unknown set key: %s", key)

    def _parse_bool(self, payload: str) -> bool:
        s = payload.lower()
        if s in ("on", "1", "true", "yes", "locked"):
            return True
        if s in ("off", "0", "false", "no", "unlocked"):
            return False
        # fallback: try numeric
        try:
            return float(payload) != 0.0
        except Exception:
            return False

    def on_message(self, client, userdata, msg):
        topic_parts = msg.topic.split("/")
        # expect: prefix/serial/<key>/set  OR prefix/serial/<key>
        # we'll only react to /set topics
        if not msg.topic.startswith(self.base + "/"):
            return
        tail = msg.topic[len(self.base) + 1 :]
        if tail.endswith("/set"):
            key = tail[: -4]
            payload = msg.payload.decode("utf-8") if msg.payload else ""
            self.handle_set_message(key, payload)
        else:
            # ignore other topics for now
            _LOGGER.debug("Ignoring message on %s", msg.topic)

    def start(self):
        # subscribe to all command topics
        for k in TEXT_TYPES + SWITCH_TYPES + SELECT_TYPES:
            ct = command_topic(self.base, k)
            self.client.subscribe(ct)
            _LOGGER.debug("Subscribed to %s", ct)

        # publish retained initial states
        self.publish_all_initial()

        self.running = True

        def loop():
            while self.running:
                self._publish_telemetry_cycle()
                time.sleep(self.interval)

        t = threading.Thread(target=loop, daemon=True)
        t.start()

    def stop(self):
        self.running = False

    def _publish_telemetry_cycle(self):
        # simulate small fluctuations
        with self.lock:
            # temperature float
            temp = float(self.state.get("temperature", 25.0))
            temp += random.uniform(-0.2, 0.2)
            self.state["temperature"] = round(temp, 2)
            self.publish_retained("temperature", self.state["temperature"])
            # pH with one decimal
            ph = float(self.state.get("ph", 7.2))
            ph += random.uniform(-0.05, 0.05)
            self.state["ph"] = round(ph, 1)
            self.publish_retained("ph", f"{self.state['ph']:.1f}")

            # chlorine as float with 3 decimals
            chlorine = float(self.state.get("chlorine", 0.802))
            chlorine += random.uniform(-0.005, 0.005)
            self.state["chlorine"] = round(chlorine, 3)
            self.publish_retained("chlorine", f"{self.state['chlorine']:.3f}")

            # textual/status sensors
            # water_level: ok/nok
            self.state["water_level"] = random.choice(["ok", "nok"])
            self.publish_retained("water_level", self.state["water_level"])

            # chlorine_level / ph_level options
            self.state["chlorine_level"] = random.choice(["low", "no liquid", "ok"])
            self.publish_retained("chlorine_level", self.state["chlorine_level"])

            self.state["ph_level"] = random.choice(["low", "no liquid", "ok"])
            self.publish_retained("ph_level", self.state["ph_level"])

            # informational values (dates formatted DD/MM/YY HH:MM)
            from datetime import datetime

            now = datetime.now()
            self.state["last_pH_prob_cal"] = now.strftime("%d/%m/%y %H:%M")
            self.state["last_ORP_prob_cal"] = now.strftime("%d/%m/%y %H:%M")
            self.state["last_pump_cleaning"] = now.strftime("%d/%m/%y %H:%M")
            self.publish_retained("last_pH_prob_cal", self.state["last_pH_prob_cal"])
            self.publish_retained("last_ORP_prob_cal", self.state["last_ORP_prob_cal"])
            self.publish_retained("last_pump_cleaning", self.state["last_pump_cleaning"])

            # firmware & availability
            self.publish_retained("firmware", self.state.get("firmware", "1.0.0"))
            self.publish_retained("availability", self.state.get("availability", "online"))

            # alert as JSON
            alert = {"type": "none", "message": "", "timestamp": now.isoformat()}
            self.state["alert"] = json.dumps(alert, ensure_ascii=False)
            self.publish_retained("alert", self.state["alert"])

            # re-publish switches/select/text states to reflect any changes
            for k in TEXT_TYPES:
                self.publish_retained(k, self.state.get(k, ""))
            for k in SWITCH_TYPES:
                self.publish_retained(k, "ON" if self.state.get(k) else "OFF")
            for k in SELECT_TYPES:
                self.publish_retained(k, self.state.get(k, ""))


def main():
    parser = argparse.ArgumentParser(description="PoolNexus MQTT simulator")
    parser.add_argument("--host", default="127.0.0.1", help="MQTT broker host")
    parser.add_argument("--port", type=int, default=1883, help="MQTT broker port")
    parser.add_argument("--username", help="MQTT username", default=None)
    parser.add_argument("--password", help="MQTT password", default=None)
    parser.add_argument("--prefix", default=DEFAULT_PREFIX, help="topic prefix (e.g. poolnexus)")
    parser.add_argument("--serial", required=True, help="device serial to include in topics")
    parser.add_argument("--interval", type=float, default=10.0, help="telemetry publish interval seconds")
    parser.add_argument("--client-id", default=None, help="MQTT client id (optional)")
    parser.add_argument("--debug", action="store_true", help="enable debug logging")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    # Some paho-mqtt versions emit a DeprecationWarning about callback API
    # version 1. Trying to force a newer API can cause a runtime error on
    # older installs. To be robust across environments we:
    # 1) create the client using the default constructor and
    # 2) suppress the specific DeprecationWarning so logs stay clean.
    warnings.filterwarnings(
        "ignore",
        message=r".*Callback API version 1 is deprecated.*",
        category=DeprecationWarning,
    )

    client = mqtt.Client(client_id=args.client_id) if args.client_id else mqtt.Client()

    # Resolve username/password from (in order): CLI args -> environment -> prompt
    username = args.username or os.environ.get("MQTT_USERNAME")
    password = args.password or os.environ.get("MQTT_PASSWORD")
    if username and not password:
        # Prompt for password interactively (doesn't show on terminal)
        try:
            password = getpass.getpass(f"MQTT password for '{username}': ")
        except Exception:
            password = None

    if username:
        # If password is None, username_pw_set still accepts None and will try
        # to connect without a password (broker may reject it).
        client.username_pw_set(username, password)

    sim = PoolNexusSimulator(client, args.prefix, args.serial, interval=args.interval)

    def _on_connect(client, userdata, flags, rc):
        if rc == 0:
            _LOGGER.info("Connected to MQTT broker %s:%s", args.host, args.port)
        else:
            _LOGGER.error("MQTT connection failed with rc=%s", rc)

    client.on_connect = _on_connect
    client.on_message = sim.on_message

    try:
        client.connect(args.host, args.port)
    except Exception as exc:
        _LOGGER.exception("Failed to connect to broker: %s", exc)
        return

    client.loop_start()
    try:
        sim.start()
        _LOGGER.info("Simulator running (prefix=%s, serial=%s). Press Ctrl-C to stop.", args.prefix, args.serial)
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        _LOGGER.info("Stopping simulator...")
    finally:
        sim.stop()
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
