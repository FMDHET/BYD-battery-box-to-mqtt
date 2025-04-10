
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
                   
