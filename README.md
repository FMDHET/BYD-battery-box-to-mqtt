# BYD Battery Box (Gen 2) to MQTT 

![BYD_Battery_Evolution](https://github.com/user-attachments/assets/eb15220b-9607-4d9e-9716-d18a79a327cc)


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

<img width="1114" alt="BYD-Battery-Box" src="https://github.com/user-attachments/assets/e8dc939f-5725-401a-91ac-5c87b0ff2dd5" />

<img width="401" alt="Array" src="https://github.com/user-attachments/assets/7ea4fbed-ab8b-4d03-975c-8d84f6764d16" />

<img width="785" alt="Battery-Module" src="https://github.com/user-attachments/assets/6d71ffbb-eb86-4542-b019-ed9e03182beb" />
