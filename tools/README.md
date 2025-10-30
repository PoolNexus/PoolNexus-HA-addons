MQTT PoolNexus simulator

This folder contains a small MQTT simulator that mimics a PoolNexus device
by publishing telemetry and responding to `/.../set` topics used by Home
Assistant.

Quick usage (PowerShell):

- Install dependency:

```powershell
python -m pip install paho-mqtt
```

- Run with username/password on the command line (visible in history):

```powershell
python tools\mqtt_poolnexus_simulator.py --host 192.168.56.101 --port 1883 --prefix poolnexus --serial SIM12345 --username myuser --password mypass
```

- Or export environment variables (safer):

```powershell
$env:MQTT_USERNAME='myuser'
$env:MQTT_PASSWORD='mypassword'
python tools\mqtt_poolnexus_simulator.py --host 192.168.56.101 --prefix poolnexus --serial SIM12345
```

- Or provide only `--username` to be prompted for the password interactively:

```powershell
python tools\mqtt_poolnexus_simulator.py --host 192.168.56.101 --prefix poolnexus --serial SIM12345 --username myuser
```

Notes:
- The simulator publishes retained telemetry under topics like
  `poolnexus/SIM12345/temperature` and listens to `poolnexus/SIM12345/<key>/set`.
- Use `--interval` to change the telemetry publish interval (default 10s).
