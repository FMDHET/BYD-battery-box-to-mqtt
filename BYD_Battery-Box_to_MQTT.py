
import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import paho.mqtt.client as mqtt

# --- Konfiguration ---
BATTERIES_PER_ARRAY = 6

# --- MQTT CONFIG ---
MQTT_BROKER = "192.168.177.xx"                # <--- Set your MQTT IP address here
MQTT_PORT = 1883
MQTT_USER = "your_user"                       # <--- Set your MQTT user here
MQTT_PASSWORD = "your_password"               # <--- Set your MQTT password here
TOPIC_BATTERY = "homeassistant/sensor/BYD/Battery"
DISCOVERY_PREFIX = "homeassistant"

PUBLISH_INTERVAL = 15
DISCOVERY_INTERVAL = 600

# --- BYD CONFIG ---
BATTERY_IP = "192.168.177.xx"                 # <--- Set your Battery Box IP address here
url = f"http://{BATTERY_IP}/asp/RunData.asp"
username = "installer"
password = "byd@12345"

# --- MQTT Setup ---
client = mqtt.Client()
client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)

def publish_discovery(sensor_key, name, topic_path, unit=None, device_class=None, state_class=None):
    unique_id = f"byd_{sensor_key}".lower()
    state_topic = f"{topic_path}/{sensor_key}"
    discovery_topic = f"{DISCOVERY_PREFIX}/sensor/{unique_id}/config"
    payload = {
        "name": name,
        "state_topic": state_topic,
        "unique_id": unique_id,
        "device": {
            "identifiers": ["byd_battery_box"],
            "manufacturer": "BYD",
            "model": "Battery Box",
            "name": "BYD Battery"
        }
    }
    if unit: payload["unit_of_measurement"] = unit
    if device_class: payload["device_class"] = device_class
    if state_class: payload["state_class"] = state_class
    client.publish(discovery_topic, json.dumps(payload), retain=True)

def parse_battery_data(html, battery_num):
    soup = BeautifulSoup(html, "html.parser")
    inputs = soup.find_all("input")
    battery_data = {}

    allowed_labels = [
        "BattVol", "CellVolDiff",
        "CellVolMax", "CellVolMin"
    ] + [f"CellVol[{i}]" for i in range(1, 17)] + [f"CellTemp[{i}]" for i in range(1, 5)]

    for input_elem in inputs:
        if input_elem.has_attr("value") and input_elem["type"] == "text":
            parent = input_elem.find_parent("td").find_previous_sibling("td")
            if parent:
                label = parent.get_text(strip=True).strip(":")
                if label not in allowed_labels:
                    continue
                value = input_elem.get("value", "").strip()
                label_raw = label
                if "CellVol[" in label or "CellTemp[" in label:
                    prefix = label.split("[")[0]
                    num = int(label.split("[")[1].replace("]", ""))
                    num_str = f"{num:02}" if num < 10 else str(num)
                    key_base = f"{prefix}_{num_str}"
                else:
                    key_base = label.replace("[", "_").replace("]", "")
                parts = key_base.split("_")
                if len(parts) == 2:
                    key = f"{parts[0]}_B{battery_num}_{parts[1]}"
                else:
                    key = f"{key_base}_B{battery_num}"
                battery_data[key] = value
    return battery_data

def parse_array_data(html):
    soup = BeautifulSoup(html, "html.parser")
    inputs = soup.find_all("input")
    array_data = {}
    for input_elem in inputs:
        if input_elem.has_attr("value") and input_elem["type"] == "text":
            parent = input_elem.find_parent("td").find_previous_sibling("td")
            if parent:
                label = parent.get_text(strip=True).strip(":")
                if label in ["ArrayVoltage", "SOC", "Power", "Current"]:
                    value = input_elem.get("value", "").strip()
                    key = f"{label}_A1"
                    array_data[key] = value
    return array_data

print("📡 Starte MQTT (reduzierte Batterie-Daten + Array 1)")

last_discovery = 0

while True:
    battery_data = {}
    discovery_now = (time.time() - last_discovery > DISCOVERY_INTERVAL)

    # Array 1 abrufen
    try:
        r = requests.post(url, auth=HTTPBasicAuth(username, password), data={"ArrayNum": "1"}, timeout=10)
        r.raise_for_status()
        array_data = parse_array_data(r.text)
    except Exception as e:
        print(f"⚠️ Fehler beim Array 1: {e}")
    else:
        for key, value in array_data.items():
            topic = f"{TOPIC_BATTERY}/{key}"
            try:
                if value.endswith("%"):
                    value = value.replace("%", "")
                value = float(value)
                client.publish(topic, json.dumps(value))
            except:
                client.publish(topic, value)

            if discovery_now:
                unit = None
                if "Voltage" in key: unit = "V"
                elif "Current" in key: unit = "A"
                elif "Temp" in key: unit = "°C"
                elif "SOC" in key: unit = "%"
                elif "Power" in key: unit = "kW"

                device_class = None
                if "Temp" in key: device_class = "temperature"
                elif "Voltage" in key: device_class = "voltage"
                elif "Current" in key: device_class = "current"
                elif "Power" in key: device_class = "power"

                name = key.replace("_", " ")
                publish_discovery(
                    sensor_key=key,
                    name=name,
                    topic_path=TOPIC_BATTERY,
                    unit=unit,
                    device_class=device_class,
                    state_class="measurement"
                )

    for battery_num in range(1, BATTERIES_PER_ARRAY + 1):
        try:
            r = requests.post(url, auth=HTTPBasicAuth(username, password),
                              data={"SeriesBatteryNum": str(battery_num)}, timeout=10)
            r.raise_for_status()
            html = r.text
            data = parse_battery_data(html, battery_num)
            for k, v in data.items():
                battery_data[k] = v
        except Exception as e:
            print(f"⚠️ Fehler bei Batterie {battery_num}: {e}")

    timestamp = datetime.now().isoformat()

    for key, value in battery_data.items():
        topic = f"{TOPIC_BATTERY}/{key}"
        try:
            if False:
                client.publish(topic, value)
                if discovery_now:
                    publish_discovery(
                        sensor_key=key,
                        name=key.replace("_", " "),
                        topic_path=TOPIC_BATTERY,
                        unit=None,
                        device_class=None,
                        state_class=None
                    )
                continue
            if value.endswith("%"):
                value = value.replace("%", "")
            value = float(value)
            client.publish(topic, json.dumps(value))
        except:
            client.publish(topic, value)

        if discovery_now:
            unit = None
            if "CellVol" in key or "BattVol" in key: unit = "V"
            elif "CellTemp" in key: unit = "°C"

            device_class = None
            if "Temp" in key: device_class = "temperature"
            elif "Vol" in key: device_class = "voltage"

            name = key.replace("_", " ")
            publish_discovery(
                sensor_key=key,
                name=name,
                topic_path=TOPIC_BATTERY,
                unit=unit,
                device_class=device_class,
                state_class="measurement"
            )

    if discovery_now:
        last_discovery = time.time()

    print(f"✅ Daten gesendet: {timestamp}")
    time.sleep(PUBLISH_INTERVAL)
             
