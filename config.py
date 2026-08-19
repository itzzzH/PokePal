import json
import time
import copy
from pathlib import Path

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "hub_opacity": 90,
    "counter_bg": "#1E1E24",
    "counter_opacity": 85,
    "counter_text_color": "#E2E2E8",
    "counter_text_alpha": 100,
    "counter_num_color": "#80A0FF",
    "counter_num_alpha": 100,
    "hub_visible": True,
    "counter_visible": False,
    "pokedex_visible": False,
    "breeding_visible": False,
    "timers_visible": False,
    "weakness_visible": False,
    "sticky_note_visible": False,
    "locations_visible": False,
    "counter_rows": [
        {"name": "change me",
         "count": 0,
          "sprite_folder": "items",
           "sprite_id": "1"}
    ],
    "timer_rows": [
        {
            "name": "Gym Rerun",
            "duration": 18 * 3600,
            "remaining": 18 * 3600,
            "is_running": False,
            "expired": False,
            "last_updated": time.time(),
            "sprite_folder": "items",
            "sprite_id": "5444",
        },
        {
            "name": "Berries (8h)",
            "duration": 8 * 3600,
            "remaining": 8 * 3600,
            "is_running": False,
            "expired": False,
            "last_updated": time.time(),
            "sprite_folder": "items",
            "sprite_id": "5154",
        },
    ],
    "hub_pos": [955, 959],
    "counter_pos": [1568, 527],
    "pokedex_pos": [450, 100],
    "breeding_pos": [200, 200],
    "timers_pos": [1567, 431],
    "weakness_pos": [350, 250],
    "sticky_note_pos": [400, 200],
    "locations_pos": [400, 200],
    "counter_size": [202, 57],
    "pokedex_size": [480, 720],
    "breeding_size": [720, 480],
    "timers_size": [203, 96],
    "weakness_size": [360, 480],
    "sticky_note_size": [280, 300],
    "locations_size": [540, 560],
}

def load_config():
    config_path = Path(CONFIG_FILE)
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for key, val in DEFAULT_CONFIG.items():
                    if key not in data:
                        data[key] = copy.deepcopy(val)
                return data
        except Exception as e:
            print(f"Error loading configuration: {e}")

    return copy.deepcopy(DEFAULT_CONFIG)

def save_config(data):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving configuration: {e}")