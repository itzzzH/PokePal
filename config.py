# config.py
import json
import os

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "hub_opacity": 90,
    "counter_bg": "#1E1E24", "counter_opacity": 85, 
    "counter_text_color": "#E2E2E8", "counter_text_alpha": 100,
    "counter_num_color": "#80A0FF", "counter_num_alpha": 100,
    "counter_rows": [
        {"name": "Encounters", "count": 0},
        {"name": "Phases", "count": 1},
        {"name": "Target Shinies", "count": 0}
    ],
    "hub_pos": [100, 100],
    "counter_pos": [180, 100],
    "pokedex_pos": [450, 100],
    "breeding_pos": [200, 200],
    "counter_size": [260, 150],
    "pokedex_size": [480, 720],
    "breeding_size": [720, 480]
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for key in DEFAULT_CONFIG:
                    if key not in data:
                        data[key] = DEFAULT_CONFIG[key]
                return data
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()

def save_config(data):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception:
        pass