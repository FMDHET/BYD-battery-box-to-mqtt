# BYD Battery Box (Gen 2) to MQTT 

![BYD_Battery_Evolution](https://github.com/user-attachments/assets/9f16f637-c7ba-4ec7-b614-82f2f84f69e3)


This Python script reads battery and array data from a BYD Battery Box via HTTP and publishes the values to an MQTT broker. It is designed for easy integration with [Home Assistant](https://www.home-assistant.io/) via MQTT Discovery.

## Features

- 🔌 Connects to a BYD Battery Box using HTTP Basic Authentication
- 📡 Parses key metrics like:
  - `BattVol`, `CellVol[1-16]`, `CellTemp[1-4]`
  - `SOC`, `Current`, `Power`, `ArrayVoltage`
- 📤 Publishes values to a configurable MQTT broker
- 🏠 Automatically registers all sensors via Home Assistant MQTT Discovery
- 🔁 Configurable polling interval
- 🌐 Battery IP address is configurable via a single variable (`BATTERY_IP`)

## Configuration

Update the following section in the script to match your setup:

```python
# --- BYD CONFIG ---
BATTERY_IP = "192.168.177.xx"  # <--- Set your Battery Box IP address here
url = f"http://{BATTERY_IP}/asp/RunData.asp"
username = "installer"
password = "byd@12345"


# --- MQTT CONFIG ---
MQTT_BROKER = "192.168.177.xx"  # <--- Set your Battery Box IP address here
MQTT_PORT = 1883
MQTT_USER = "your_user"
MQTT_PASSWORD = "your_password"
```

## Requirements

Install the required Python packages:

```requirements
pip install requests beautifulsoup4 paho-mqtt
```

## Usage

Run the script:

```usage
python BYD_Battery-Box_to_MQTT.py
```

## Installation on debian

```ìnstall
apt update
apt install python3 python3-pip -y
pip3 install paho-mqtt requests beautifulsoup4

mkdir -p /opt/byd_mqtt
nano /opt/byd_mqtt/BYD_Battery-Box_to_MQTT.py
```

Setup the script according you needs. e.g. IP adresses, mqtt user, password.

```setup daemon
nano /etc/systemd/system/byd.service
```

```content daemon
[Unit]
Description=BYD Battery Box to MQTT
After=network.target

[Service]
ExecStart=/usr/bin/python3 /opt/byd_mqtt/BYD_Battery-Box_to_MQTT.py
WorkingDirectory=/opt/byd_mqtt
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

```start daemon
systemctl daemon-reexec
systemctl daemon-reload
systemctl enable byd.service
systemctl start byd.service
```

```debug daemon
systemctl status byd.service
journalctl -u byd.service -f
```




## Overview BYD-Webinterface

<img width="704" alt="BYD-Battery-Box" src="https://github.com/user-attachments/assets/e8dc939f-5725-401a-91ac-5c87b0ff2dd5" />

<img width="350" alt="Array" src="https://github.com/user-attachments/assets/7ea4fbed-ab8b-4d03-975c-8d84f6764d16" />

<img width="350" alt="![Battery-Module]" src="https://github.com/user-attachments/assets/39a54fe5-4112-488b-9caa-e95a85e6ed37" />




## Home Assistant - MQTT Discovery


<img width="704" alt="HA-MQTT" src="https://github.com/user-attachments/assets/5c41f5ac-22fb-4a60-be78-df34a82b2607" />


