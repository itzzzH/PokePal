import sys
import time
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


class MainAppController:

  def __init__(self):
    # --- Prevent overwriting visibility during startup ---
    self._initializing = True

    # 1. Load configuration
    self.config = load_config()

    self.hub_opacity = self.config.get("hub_opacity", 90)
    self.counter_bg = self.config.get("counter_bg", "#1E1E24")
    self.counter_opacity = self.config.get("counter_opacity", 85)
    self.counter_text_color = self.config.get("counter_text_color", "#E2E2E8")
    self.counter_text_alpha = self.config.get("counter_text_alpha", 100)
    self.counter_num_color = self.config.get("counter_num_color", "#80A0FF")
    self.counter_num_alpha = self.config.get("counter_num_alpha", 100)

    self.counter_rows = self.config.get(
        "counter_rows", DEFAULT_CONFIG["counter_rows"]
    )
    self.timer_rows = self.config.get(
        "timer_rows",
        [
            {
                "name": "Gym Rerun",
                "duration": 18 * 3600,
                "remaining": 18 * 3600,
                "is_running": False,
                "expired": False,
                "last_updated": time.time(),
                "sprite_folder": "pokemon",
                "sprite_id": "145",
            },
            {
                "name": "Berry Farm",
                "duration": 8 * 3600,
                "remaining": 8 * 3600,
                "is_running": False,
                "expired": False,
                "last_updated": time.time(),
                "sprite_folder": "items",
                "sprite_id": "1",
            },
        ],
    )

    # 2. Load databases
    data_manager.load_all_databases()

    # 3. Initialize widgets
    self.hub = PokeballHub(self)
    self.counter = CounterWidget(self)
    self.pokedex = PokedexWidget(self)
    self.breeding = BreedingCalculatorWidget(self)
    self.timers = TimersWidget(self)
    self.weakness = WeaknessWidget(self)
    self.notepad = NotepadWidget(self)
    self.settings_window = None

    self.counter.update_style(
        self.counter_bg,
        self.counter_opacity,
        self.counter_text_color,
        self.counter_text_alpha,
        self.counter_num_color,
        self.counter_num_alpha,
    )

    # --- RESTORE WIDGET VISIBILITY ---
    self.hub.setVisible(self.config.get("hub_visible", True))
    self.counter.setVisible(self.config.get("counter_visible", True))
    self.pokedex.setVisible(self.config.get("pokedex_visible", False))
    self.breeding.setVisible(self.config.get("breeding_visible", False))
    self.timers.setVisible(self.config.get("timers_visible", False))
    self.weakness.setVisible(self.config.get("weakness_visible", False))
    self.notepad.setVisible(self.config.get("sticky_note_visible", False))

    if not self.hub.isVisible() and not self.counter.isVisible():
      self.hub.show()
      self.counter.show()

    # --- STARTUP FINISHED ---
    self._initializing = False

  def toggle_counter(self):
    if self.counter.isVisible():
      self.counter.hide()
    else:
      self.counter.show()
    self.save_settings()

  def toggle_pokedex(self):
    if self.pokedex.isVisible():
      self.pokedex.hide()
    else:
      self.pokedex.show()
    self.save_settings()

  def toggle_breeding(self):
    if self.breeding.isVisible():
      self.breeding.hide()
    else:
      self.breeding.show()
    self.save_settings()

  def toggle_timers(self):
    if self.timers.isVisible():
      self.timers.hide()
    else:
      self.timers.show()
    self.save_settings()

  def toggle_weakness(self):
    if self.weakness.isVisible():
      self.weakness.hide()
    else:
      self.weakness.show()
    self.save_settings()

  def toggle_notepad(self):
    if self.notepad.isVisible():
      self.notepad.hide()
    else:
      self.notepad.show()
    self.save_settings()

  def open_settings(self):
    if self.settings_window is None:
      self.settings_window = SettingsWindow(self)
    self.settings_window.show()
    self.settings_window.raise_()
    self.settings_window.activateWindow()

  def save_settings(self):
    self.config["hub_opacity"] = self.hub_opacity
    self.config["counter_bg"] = self.counter_bg
    self.config["counter_opacity"] = self.counter_opacity
    self.config["counter_text_color"] = self.counter_text_color
    self.config["counter_text_alpha"] = self.counter_text_alpha
    self.config["counter_num_color"] = self.counter_num_color
    self.config["counter_num_alpha"] = self.counter_num_alpha

    for row in self.counter_rows:
      row["name"] = row["name"].replace("▶", "").strip()
    self.config["counter_rows"] = self.counter_rows

    for row in self.timer_rows:
      row["name"] = (
          row["name"]
          .replace("▶", "")
          .replace("⏸", "")
          .replace("🚨", "")
          .strip()
      )
    self.config["timer_rows"] = self.timer_rows

    if not getattr(self, '_initializing', True):
      if getattr(self, 'hub', None):
        self.config["hub_pos"] = [self.hub.x(), self.hub.y()]
        self.config["hub_visible"] = self.hub.isVisible()
        
      if getattr(self, 'counter', None):
        self.config["counter_pos"] = [self.counter.x(), self.counter.y()]
        self.config["counter_size"] = [self.counter.width(), self.counter.height()]
        self.config["counter_visible"] = self.counter.isVisible()
        
      if getattr(self, 'pokedex', None):
        self.config["pokedex_pos"] = [self.pokedex.x(), self.pokedex.y()]
        self.config["pokedex_size"] = [self.pokedex.width(), self.pokedex.height()]
        self.config["pokedex_visible"] = self.pokedex.isVisible()
        
      if getattr(self, 'breeding', None):
        self.config["breeding_pos"] = [self.breeding.x(), self.breeding.y()]
        self.config["breeding_size"] = [
            self.breeding.width(),
            self.breeding.height(),
        ]
        self.config["breeding_visible"] = self.breeding.isVisible()
        
      if getattr(self, 'timers', None):
        self.config["timers_pos"] = [self.timers.x(), self.timers.y()]
        self.config["timers_size"] = [self.timers.width(), self.timers.height()]
        self.config["timers_visible"] = self.timers.isVisible()
        
      if getattr(self, 'weakness', None):
        self.config["weakness_pos"] = [self.weakness.x(), self.weakness.y()]
        self.config["weakness_size"] = [
            self.weakness.width(),
            self.weakness.height(),
        ]
        self.config["weakness_visible"] = self.weakness.isVisible()

      if getattr(self, 'notepad', None):
        self.config["sticky_note_pos"] = [self.notepad.x(), self.notepad.y()]
        self.config["sticky_note_size"] = [
            self.notepad.width(),
            self.notepad.height(),
        ]
        self.config["sticky_note_visible"] = self.notepad.isVisible()

    save_config(self.config)


if __name__ == "__main__":
  app = QApplication(sys.argv)
  app.setQuitOnLastWindowClosed(False)
  app.setStyleSheet(MODERN_DARK_STYLESHEET)

  main_app = MainAppController()
  sys.exit(app.exec())