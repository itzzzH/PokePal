# widgets/settings.py
import time
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTabWidget, QSlider, QScrollArea, QGroupBox
)
from core.utils import clean_count

class SettingsWindow(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.setWindowTitle("PokePal - Settings")
        self.resize(760, 580)
        
        # Ensure the settings window always floats above other tool overlays
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint
        )
        
        self.init_ui()
        self.show()
        self.raise_()
        self.activateWindow()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        # Discard un-saved changes (such as un-saved added rows) when closing via X
        self.revert_to_saved_state()

    def revert_to_saved_state(self):
        while self.c_rows_layout.count():
            item = self.c_rows_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.populate_counter_fields()

        while self.t_rows_layout.count():
            item = self.t_rows_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.populate_timer_fields()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()

        # --- COUNTER TAB ---
        self.counter_tab = QWidget()
        c_layout = QVBoxLayout(self.counter_tab)
        
        c_rows_group = QGroupBox("Counter Rows Configuration (Name, Count, Folder & ID)")
        self.c_rows_scroll = QScrollArea()
        self.c_rows_scroll.setWidgetResizable(True)
        self.c_rows_content = QWidget()
        self.c_rows_layout = QVBoxLayout(self.c_rows_content)
        self.c_rows_scroll.setWidget(self.c_rows_content)
        
        cr_box_l = QVBoxLayout(c_rows_group)
        cr_box_l.addWidget(self.c_rows_scroll)
        c_layout.addWidget(c_rows_group, 1)

        c_btns = QHBoxLayout()
        btn_add_c = QPushButton("Add Row")
        btn_add_c.clicked.connect(self.add_counter_row_ui)
        btn_reset_c = QPushButton("Reset Counts")
        btn_reset_c.clicked.connect(lambda: self.main_app.counter.reset_all() if hasattr(self.main_app.counter, 'reset_all') else None)
        c_btns.addWidget(btn_add_c)
        c_btns.addWidget(btn_reset_c)
        c_layout.addLayout(c_btns)

        self.tabs.addTab(self.counter_tab, "Counter")
        self.populate_counter_fields()

        # --- TIMERS TAB ---
        self.timers_tab = QWidget()
        t_layout = QVBoxLayout(self.timers_tab)
        
        t_rows_group = QGroupBox("Timers Configuration (Name, Duration, Sprite Folder & ID)")
        self.t_rows_scroll = QScrollArea()
        self.t_rows_scroll.setWidgetResizable(True)
        self.t_rows_content = QWidget()
        self.t_rows_layout = QVBoxLayout(self.t_rows_content)
        self.t_rows_scroll.setWidget(self.t_rows_content)
        
        tr_box_l = QVBoxLayout(t_rows_group)
        tr_box_l.addWidget(self.t_rows_scroll)
        t_layout.addWidget(t_rows_group, 1)

        t_btns = QHBoxLayout()
        btn_add_t = QPushButton("Add Timer")
        btn_add_t.clicked.connect(self.add_timer_row_ui)
        t_btns.addWidget(btn_add_t)
        t_layout.addLayout(t_btns)

        self.tabs.addTab(self.timers_tab, "Timers")
        self.populate_timer_fields()

        # --- THEME & STYLE TAB ---
        theme_scroll = QScrollArea()
        theme_scroll.setWidgetResizable(True)
        theme_content = QWidget()
        theme_layout = QVBoxLayout(theme_content)

        hub_group = QGroupBox("Pokeball Hub Overlay")
        hub_layout = QVBoxLayout(hub_group)
        hub_layout.addWidget(QLabel("Hub Opacity:"))
        self.hub_opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.hub_opacity_slider.setRange(10, 100)
        self.hub_opacity_slider.setValue(getattr(self.main_app, 'hub_opacity', 90))
        self.hub_opacity_slider.valueChanged.connect(self.apply_theme_preview)
        hub_layout.addWidget(self.hub_opacity_slider)
        theme_layout.addWidget(hub_group)

        # Counter Theme Group
        counter_theme_group = QGroupBox("Counter Overlay Theme")
        ct_layout = QVBoxLayout(counter_theme_group)
        
        ct_layout.addWidget(QLabel("Background Color:"))
        self.c_bg_hex = QLineEdit(getattr(self.main_app, 'counter_bg', '#1E1E24'))
        self.c_bg_hex.textChanged.connect(self.apply_theme_preview)
        ct_layout.addWidget(self.c_bg_hex)

        ct_layout.addWidget(QLabel("Background Opacity (Min 10%):"))
        self.c_opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.c_opacity_slider.setRange(10, 100)
        self.c_opacity_slider.setValue(getattr(self.main_app, 'counter_opacity', 90))
        self.c_opacity_slider.valueChanged.connect(self.apply_theme_preview)
        ct_layout.addWidget(self.c_opacity_slider)

        ct_layout.addWidget(QLabel("Text Color:"))
        self.c_text_hex = QLineEdit(getattr(self.main_app, 'counter_text_color', '#E2E2E8'))
        self.c_text_hex.textChanged.connect(self.apply_theme_preview)
        ct_layout.addWidget(self.c_text_hex)

        ct_layout.addWidget(QLabel("Numbers Color:"))
        self.c_num_hex = QLineEdit(getattr(self.main_app, 'counter_num_color', '#80A0FF'))
        self.c_num_hex.textChanged.connect(self.apply_theme_preview)
        ct_layout.addWidget(self.c_num_hex)
        theme_layout.addWidget(counter_theme_group)

        # Timers Theme Group
        timers_theme_group = QGroupBox("Timers Overlay Theme")
        dt_layout = QVBoxLayout(timers_theme_group)
        
        dt_layout.addWidget(QLabel("Background Color:"))
        self.t_bg_hex = QLineEdit(getattr(self.main_app, 'timer_bg', getattr(self.main_app, 'counter_bg', '#1E1E24')))
        self.t_bg_hex.textChanged.connect(self.apply_theme_preview)
        dt_layout.addWidget(self.t_bg_hex)

        dt_layout.addWidget(QLabel("Background Opacity (Min 10%):"))
        self.t_opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.t_opacity_slider.setRange(10, 100)
        self.t_opacity_slider.setValue(getattr(self.main_app, 'timer_opacity', getattr(self.main_app, 'counter_opacity', 90)))
        self.t_opacity_slider.valueChanged.connect(self.apply_theme_preview)
        dt_layout.addWidget(self.t_opacity_slider)

        dt_layout.addWidget(QLabel("Text Color:"))
        self.t_text_hex = QLineEdit(getattr(self.main_app, 'timer_text_color', getattr(self.main_app, 'counter_text_color', '#E2E2E8')))
        self.t_text_hex.textChanged.connect(self.apply_theme_preview)
        dt_layout.addWidget(self.t_text_hex)

        dt_layout.addWidget(QLabel("Numbers Color:"))
        self.t_num_hex = QLineEdit(getattr(self.main_app, 'timer_num_color', getattr(self.main_app, 'counter_num_color', '#80A0FF')))
        self.t_num_hex.textChanged.connect(self.apply_theme_preview)
        dt_layout.addWidget(self.t_num_hex)
        theme_layout.addWidget(timers_theme_group)

        theme_scroll.setWidget(theme_content)
        self.tabs.addTab(theme_scroll, "Theme Style")

        layout.addWidget(self.tabs)

        bot_layout = QHBoxLayout()
        btn_save = QPushButton("Save Settings")
        btn_save.clicked.connect(self.save_settings)
        bot_layout.addWidget(btn_save)
        layout.addLayout(bot_layout)

    def apply_theme_preview(self):
        self.main_app.hub_opacity = self.hub_opacity_slider.value()
        if hasattr(self.main_app, 'hub'):
            self.main_app.hub.update_style()
        
        # Apply Counter Theme
        self.main_app.counter_bg = self.c_bg_hex.text().strip() or "#1E1E24"
        self.main_app.counter_opacity = self.c_opacity_slider.value()
        self.main_app.counter_text_color = self.c_text_hex.text().strip() or "#E2E2E8"
        self.main_app.counter_num_color = self.c_num_hex.text().strip() or "#80A0FF"
        
        if hasattr(self.main_app, 'counter'):
            self.main_app.counter.update_style(
                self.main_app.counter_bg, self.main_app.counter_opacity,
                self.main_app.counter_text_color, getattr(self.main_app, 'counter_text_alpha', 100),
                self.main_app.counter_num_color, getattr(self.main_app, 'counter_num_alpha', 100)
            )

        # Apply Timers Theme
        self.main_app.timer_bg = self.t_bg_hex.text().strip() or "#1E1E24"
        self.main_app.timer_opacity = self.t_opacity_slider.value()
        self.main_app.timer_text_color = self.t_text_hex.text().strip() or "#E2E2E8"
        self.main_app.timer_num_color = self.t_num_hex.text().strip() or "#80A0FF"

        if hasattr(self.main_app, 'timers'):
            self.main_app.timers.update_style(
                self.main_app.timer_bg, self.main_app.timer_opacity,
                self.main_app.timer_text_color, getattr(self.main_app, 'timer_text_alpha', 100),
                self.main_app.timer_num_color, getattr(self.main_app, 'timer_num_alpha', 100)
            )

    def populate_counter_fields(self):
        self.counter_inputs = []
        if not hasattr(self.main_app, "counter_rows") or not self.main_app.counter_rows:
            self.main_app.counter_rows = [
                {"name": "Encounters", "count": 0, "sprite_folder": "pokemon", "sprite_id": "25"}
            ]
        for row in self.main_app.counter_rows:
            self.add_counter_row_ui(row)

    def add_counter_row_ui(self, row_data=None):
        name = row_data.get("name", "New Counter") if isinstance(row_data, dict) else "New Counter"
        count = row_data.get("count", 0) if isinstance(row_data, dict) else 0
        sprite_folder = row_data.get("sprite_folder", "pokemon") if isinstance(row_data, dict) else "pokemon"
        sprite_id = str(row_data.get("sprite_id", "")) if isinstance(row_data, dict) else ""

        row_widget = QWidget()
        r_layout = QHBoxLayout(row_widget)
        r_layout.setContentsMargins(0, 0, 0, 0)

        name_input = QLineEdit(name)
        count_input = QLineEdit(str(count))
        count_input.setFixedWidth(60)
        
        folder_btn = QPushButton(sprite_folder)
        folder_btn.setFixedWidth(90)
        def toggle_folder():
            current = folder_btn.text()
            folder_btn.setText("items" if current == "pokemon" else "pokemon")
        folder_btn.clicked.connect(toggle_folder)

        id_input = QLineEdit(sprite_id)
        id_input.setPlaceholderText("ID #")
        id_input.setFixedWidth(60)

        btn_del = QPushButton("Delete")
        btn_del.clicked.connect(lambda: row_widget.setParent(None) or self.counter_inputs.remove((name_input, count_input, folder_btn, id_input, row_widget)))

        r_layout.addWidget(name_input, 1)
        r_layout.addWidget(count_input)
        r_layout.addWidget(folder_btn)
        r_layout.addWidget(id_input)
        r_layout.addWidget(btn_del)

        self.c_rows_layout.addWidget(row_widget)
        self.counter_inputs.append((name_input, count_input, folder_btn, id_input, row_widget))

    def populate_timer_fields(self):
        self.timer_inputs = []
        if not hasattr(self.main_app, "timer_rows"):
            self.main_app.timer_rows = [
                {"name": "Gym Rerun", "duration": 18 * 3600, "remaining": 18 * 3600, "is_running": False, "sprite_folder": "pokemon", "sprite_id": "145"},
                {"name": "Berry Farm", "duration": 8 * 3600, "remaining": 8 * 3600, "is_running": False, "sprite_folder": "items", "sprite_id": "1"}
            ]
        for row in self.main_app.timer_rows:
            self.add_timer_row_ui(row)

    def add_timer_row_ui(self, row_data=None):
        duration = row_data.get("duration", 3600) if isinstance(row_data, dict) else 3600
        name = row_data.get("name", "New Timer") if isinstance(row_data, dict) else "New Timer"
        duration_mins = max(1, duration // 60)
        sprite_folder = row_data.get("sprite_folder", "pokemon") if isinstance(row_data, dict) else "pokemon"
        sprite_id = str(row_data.get("sprite_id", "")) if isinstance(row_data, dict) else ""

        row_widget = QWidget()
        r_layout = QHBoxLayout(row_widget)
        r_layout.setContentsMargins(0, 0, 0, 0)

        name_input = QLineEdit(name)
        
        dur_input = QLineEdit(str(duration_mins))
        dur_input.setFixedWidth(50)
        dur_lbl = QLabel("m")
        dur_lbl.setStyleSheet("border: none; background: transparent;")

        folder_btn = QPushButton(sprite_folder)
        folder_btn.setFixedWidth(90)
        def toggle_folder():
            current = folder_btn.text()
            folder_btn.setText("items" if current == "pokemon" else "pokemon")
        folder_btn.clicked.connect(toggle_folder)

        id_input = QLineEdit(sprite_id)
        id_input.setPlaceholderText("ID #")
        id_input.setFixedWidth(60)
        
        btn_del = QPushButton("Delete")
        btn_del.clicked.connect(lambda: row_widget.setParent(None) or self.timer_inputs.remove((name_input, dur_input, folder_btn, id_input, row_widget)))

        r_layout.addWidget(name_input, 1)
        r_layout.addWidget(dur_input)
        r_layout.addWidget(dur_lbl)
        r_layout.addWidget(folder_btn)
        r_layout.addWidget(id_input)
        r_layout.addWidget(btn_del)

        self.t_rows_layout.addWidget(row_widget)
        self.timer_inputs.append((name_input, dur_input, folder_btn, id_input, row_widget))

    def save_settings(self):
        new_counter_rows = []
        for name_in, count_in, folder_btn, id_input, _ in self.counter_inputs:
            n = name_in.text().replace("▶", "").strip()
            if n:
                new_counter_rows.append({
                    "name": n,
                    "count": clean_count(count_in.text()),
                    "sprite_folder": folder_btn.text(),
                    "sprite_id": id_input.text().strip()
                })
        if new_counter_rows:
            self.main_app.counter_rows = new_counter_rows

        old_timer_rows = getattr(self.main_app, "timer_rows", [])
        new_timer_rows = []
        
        for idx, (name_in, dur_in, folder_btn, id_input, _) in enumerate(self.timer_inputs):
            n = name_in.text().replace("▶", "").replace("⏸", "").replace("🚨", "").strip()
            if n:
                try:
                    mins = int(dur_in.text().strip())
                except ValueError:
                    mins = 60
                new_duration = max(60, mins * 60)
                
                s_folder = folder_btn.text()
                s_id = id_input.text().strip()
                
                old_row = old_timer_rows[idx] if idx < len(old_timer_rows) else None
                
                if old_row and old_row.get("name") == n:
                    old_duration = old_row.get("duration", new_duration)
                    remaining = old_row.get("remaining", new_duration)
                    
                    if new_duration != old_duration:
                        diff = new_duration - old_duration
                        remaining = max(0, remaining + diff)
                    
                    new_timer_rows.append({
                        "name": n,
                        "duration": new_duration,
                        "remaining": remaining,
                        "is_running": old_row.get("is_running", False),
                        "expired": old_row.get("expired", False),
                        "last_updated": old_row.get("last_updated", time.time()),
                        "sprite_folder": s_folder,
                        "sprite_id": s_id
                    })
                else:
                    new_timer_rows.append({
                        "name": n,
                        "duration": new_duration,
                        "remaining": new_duration,
                        "is_running": False,
                        "expired": False,
                        "last_updated": time.time(),
                        "sprite_folder": s_folder,
                        "sprite_id": s_id
                    })
                    
        if new_timer_rows:
            self.main_app.timer_rows = new_timer_rows

        # Rebuild rows while preserving existing overlay width and height
        if hasattr(self.main_app, 'counter') and hasattr(self.main_app.counter, 'rebuild_rows'):
            c_w, c_h = self.main_app.counter.width(), self.main_app.counter.height()
            self.main_app.counter.rebuild_rows()
            self.main_app.counter.resize(c_w, c_h)
            
        if hasattr(self.main_app, 'timers') and hasattr(self.main_app.timers, 'rebuild_rows'):
            t_w, t_h = self.main_app.timers.width(), self.main_app.timers.height()
            self.main_app.timers.rebuild_rows()
            self.main_app.timers.resize(t_w, t_h)

        self.main_app.save_settings()
        self.hide()