import json
import os

CONFIG_FILE = "config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"ip": "192.168.1.200", "port": 4370}
    with open(CONFIG_FILE, "r") as f:
        try:
            data = json.load(f)
            return data
        except:
            return {"ip": "192.168.1.200", "port": 4370}

def save_config(ip, port=4370):
    data = {"ip": ip, "port": port}
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)
