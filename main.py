# main.py
import sys
import time
import urllib.request
import json
import threading
from PyQt6.QtWidgets import QApplication

from config import load_config, save_config, DEFAULT_CONFIG
from globals import MODERN_DARK_STYLESHEET
import data_manager

from widgets.hub import PokeballHub
from widgets.counter import CounterWidget
from widgets.pokedex import PokedexWidget
from widgets.breeding import BreedingCalculatorWidget
from widgets.timers import TimersWidget
from widgets.weakness import WeaknessWidget
from widgets.settings import SettingsWindow
from widgets.stickynotes import NotepadWidget
from widgets.locations import LocationsWidget

CURRENT_VERSION = "1.2.0"  # Update this string whenever you release a new version

class MainAppController:

    def __init__(self):
        self._initializing = True
        self.config = load_config()

        # Stylesheet & Counter Configuration
        self.hub_opacity = self.config.get("hub_opacity", 90)
        self.counter_bg = self.config.get("counter_bg", "#1E1E24")
        self.counter_opacity = self.config.get("counter_opacity", 85)
        self.counter_text_color = self.config.get("counter_text_color", "#E2E2E8")
        self.counter_text_alpha = self.config.get("counter_text_alpha", 100)
        self.counter_num_color = self.config.get("counter_num_color", "#80A0FF")
        self.counter_num_alpha = self.config.get("counter_num_alpha", 100)

        # Timers Styling Configuration
        self.timers_bg = self.config.get("timers_bg", "#1E1E24")
        self.timers_opacity = self.config.get("timers_opacity", 85)
        self.timers_text_color = self.config.get("timers_text_color", "#E2E2E8")
        self.timers_text_alpha = self.config.get("timers_text_alpha", 100)
        self.timers_num_color = self.config.get("timers_num_color", "#80A0FF")
        self.timers_num_alpha = self.config.get("timers_num_alpha", 100)

        self.counter_rows = self.config.get("counter_rows", DEFAULT_CONFIG.get("counter_rows", []))
        self.timer_rows = self.config.get("timer_rows", DEFAULT_CONFIG.get("timer_rows", []))

        # 1. Load databases
        data_manager.load_all_databases()

        # 1.5. Check for updates in the background
        self.update_available = False
        self.latest_version_url = "https://github.com/itzzzH/PokePal/releases/latest"
        threading.Thread(target=self.check_for_updates_silently, daemon=True).start()

        # 2. Register overlay widgets: {key: (instance, default_visible, saves_size)}
        self.widgets = {
            "hub": (PokeballHub(self), True, False),
            "counter": (CounterWidget(self), False, True),
            "pokedex": (PokedexWidget(self), False, True),
            "breeding": (BreedingCalculatorWidget(self), False, True),
            "timers": (TimersWidget(self), False, True),
            "weakness": (WeaknessWidget(self), False, True),
            "sticky_note": (NotepadWidget(self), False, True),
            "locations": (LocationsWidget(self), False, True),
        }

        # Instance attribute mapping for backwards compatibility
        self.hub = self.widgets["hub"][0]
        self.counter = self.widgets["counter"][0]
        self.pokedex = self.widgets["pokedex"][0]
        self.breeding = self.widgets["breeding"][0]
        self.timers = self.widgets["timers"][0]
        self.weakness = self.widgets["weakness"][0]
        self.notepad = self.widgets["sticky_note"][0]
        self.locations = self.widgets["locations"][0]
        self.settings_window = None

        # Apply counter & timer styling
        self.counter.update_style(
            self.counter_bg, self.counter_opacity,
            self.counter_text_color, self.counter_text_alpha,
            self.counter_num_color, self.counter_num_alpha
        )
        self.timers.update_style(
            self.timers_bg, self.timers_opacity,
            self.timers_text_color, self.timers_text_alpha,
            self.timers_num_color, self.timers_num_alpha
        )

        # 3. Restore Visibility based on saved config
        for key, (widget, default_vis, _) in self.widgets.items():
            widget.setVisible(self.config.get(f"{key}_visible", default_vis))

        if not self.hub.isVisible():
            self.hub.show()

        self._initializing = False

    def check_for_updates_silently(self):
        """Checks GitHub API for a newer release version."""
        url = "https://api.github.com/repos/itzzzH/PokePal/releases/latest"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "PokePal-App"})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                latest_tag = data.get("tag_name", "").strip("v")
                
                if latest_tag and latest_tag != CURRENT_VERSION:
                    self.update_available = True
                    print(f"Update available: v{latest_tag}")
        except Exception as e:
            # Silently fail so the app never hangs if offline
            pass

    def toggle_widget(self, key: str):
        if key in self.widgets:
            widget = self.widgets[key][0]
            new_vis = not widget.isVisible()
            widget.setVisible(new_vis)
            # Explicitly record visibility state here when toggled
            self.config[f"{key}_visible"] = new_vis
            self.save_settings()

    # Generic forwarding methods for context menus or actions
    def toggle_counter(self): self.toggle_widget("counter")
    def toggle_pokedex(self): self.toggle_widget("pokedex")
    def toggle_breeding(self): self.toggle_widget("breeding")
    def toggle_timers(self): self.toggle_widget("timers")
    def toggle_weakness(self): self.toggle_widget("weakness")
    def toggle_notepad(self): self.toggle_widget("sticky_note")
    def toggle_locations(self): self.toggle_widget("locations")

    def open_settings(self):
        if self.settings_window is None:
            self.settings_window = SettingsWindow(self)
        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()

    def save_settings(self):
        if self._initializing:
            return

        # Sanitize state titles without mutating underlying objects in place
        clean_counters = [
            {**r, "name": r["name"].replace("▶", "").strip()}
            for r in self.counter_rows
        ]
        clean_timers = [
            {**r, "name": r["name"].replace("▶", "").replace("⏸", "").replace("🚨", "").strip()}
            for r in self.timer_rows
        ]

        self.config.update({
            "hub_opacity": self.hub_opacity,
            "counter_bg": self.counter_bg,
            "counter_opacity": self.counter_opacity,
            "counter_text_color": self.counter_text_color,
            "counter_text_alpha": self.counter_text_alpha,
            "counter_num_color": self.counter_num_color,
            "counter_num_alpha": self.counter_num_alpha,
            "timers_bg": self.timers_bg,
            "timers_opacity": self.timers_opacity,
            "timers_text_color": self.timers_text_color,
            "timers_text_alpha": self.timers_text_alpha,
            "timers_num_color": self.timers_num_color,
            "timers_num_alpha": self.timers_num_alpha,
            "counter_rows": clean_counters,
            "timer_rows": clean_timers,
        })

        # Save widget coordinates and dimensions dynamically without overriding visibility states destructively
        for key, (widget, _, saves_size) in self.widgets.items():
            self.config[f"{key}_pos"] = [widget.x(), widget.y()]
            if saves_size:
                self.config[f"{key}_size"] = [widget.width(), widget.height()]

        save_config(self.config)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setStyleSheet(MODERN_DARK_STYLESHEET)

    main_app = MainAppController()
    
    # Hook up settings saving when the application exits
    app.aboutToQuit.connect(main_app.save_settings)

    sys.exit(app.exec())