# widgets/timers.py
import time
import os
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QPixmap
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QSizeGrip, QMenu, QApplication, QFrame
from core.base_overlay import BaseOverlay, ThemeBackgroundFrame

class TimerRowWidget(QFrame):
    def __init__(self, index, toggle_callback, parent=None):
        super().__init__(parent)
        self.index = index
        self.toggle_callback = toggle_callback

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle_callback(self.index)
        super().mousePressEvent(event)

class TimersWidget(BaseOverlay):
    def __init__(self, main_app):
        super().__init__("Timers & Reminders", main_app)
        self.active_index = 0
        
        current_time = time.time()

        # Load timer rows from config if they exist, otherwise use defaults[cite: 1]
        if hasattr(self.main_app, "config") and "timer_rows" in self.main_app.config:
            self.main_app.timer_rows = self.main_app.config["timer_rows"]
        elif not hasattr(self.main_app, "timer_rows") or not self.main_app.timer_rows:
            self.main_app.timer_rows = [
                {
                    "name": "Gym Rerun", 
                    "duration": 18 * 3600, 
                    "remaining": 18 * 3600, 
                    "is_running": False, 
                    "expired": False, 
                    "last_updated": current_time,
                    "sprite_folder": "pokemon", 
                    "sprite_id": "145"           
                },
                {
                    "name": "Berry Farm", 
                    "duration": 8 * 3600, 
                    "remaining": 8 * 3600, 
                    "is_running": False, 
                    "expired": False, 
                    "last_updated": current_time,
                    "sprite_folder": "items",    
                    "sprite_id": "1"             
                }
            ]

        # Calculate elapsed time since the app was last closed/active[cite: 1]
        for r in self.main_app.timer_rows:
            if "last_updated" not in r:
                r["last_updated"] = current_time

            if r.get("is_running", False):
                elapsed = int(current_time - r["last_updated"])
                if elapsed > 0:
                    r["remaining"] -= elapsed
                    if r["remaining"] <= 0:
                        r["remaining"] = 0
                        r["is_running"] = False
                        r["expired"] = True
            r["last_updated"] = current_time

        self.save_to_config()

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(4, 4, 4, 4)
        
        self.container = ThemeBackgroundFrame()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(8, 6, 8, 6)
        self.container_layout.setSpacing(2) # Reduced vertical spacing between rows[cite: 1]

        self.layout.addWidget(self.container)
        self.rebuild_rows(apply_saved_size=True)

        if "timers_pos" in self.main_app.config:
            x, y = self.main_app.config["timers_pos"]
            self.move(x, y)

        self.size_grip = QSizeGrip(self)
        self.size_grip.setStyleSheet("background: transparent; width: 14px; height: 14px;")

        bg = getattr(self.main_app, "timers_bg", "#1E1E24")
        opacity = getattr(self.main_app, "timers_opacity", 90)
        t_color = getattr(self.main_app, "timers_text_color", "#E2E2E8")
        t_alpha = getattr(self.main_app, "timers_text_alpha", 100)
        n_color = getattr(self.main_app, "timers_num_color", "#80A0FF")
        n_alpha = getattr(self.main_app, "timers_num_alpha", 100)
        self.update_style(bg, opacity, t_color, t_alpha, n_color, n_alpha)

        self.master_timer = QTimer(self)
        self.master_timer.setInterval(1000)
        self.master_timer.timeout.connect(self.tick_all)
        self.master_timer.start()

    def save_to_config(self):
        """Helper method to sync timer rows into the main app config."""
        if hasattr(self.main_app, "config"):
            self.main_app.config["timer_rows"] = self.main_app.timer_rows
            for save_method in ["save_config", "save_settings", "save", "save_data"]:
                if hasattr(self.main_app, save_method):
                    getattr(self.main_app, save_method)()
                    break

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.size_grip.move(self.width() - 20, self.height() - 20)

    def load_sprite_icon(self, data, lbl_icon):
        """Loads a smaller sprite pixmap (32x32) from data/sprites or data/sprites/items."""
        folder = data.get("sprite_folder", "pokemon")
        sprite_id = str(data.get("sprite_id", "")).strip()

        if sprite_id:
            if folder == "items":
                path = os.path.join("data", "sprites", "items", f"{sprite_id}.png")
            else:
                path = os.path.join("data", "sprites", f"{sprite_id}.png")

            if os.path.exists(path):
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    # Reduced sprite size from 48x48 to 32x32[cite: 1]
                    lbl_icon.setPixmap(pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                    return

        # Fallback symbols if no sprite configured or file missing (scaled up font size)[cite: 1]
        if data.get("expired", False):
            lbl_icon.setText("🚨")
        elif data.get("is_running", False):
            lbl_icon.setText("⏸")
        else:
            lbl_icon.setText("▶")
        lbl_icon.setStyleSheet("font-size: 18px; border: none; background: transparent;")

    def rebuild_rows(self, apply_saved_size=False):
        for i in reversed(range(self.container_layout.count())):
            item = self.container_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)

        self.row_widgets = []
        for idx, data in enumerate(self.main_app.timer_rows):
            if "remaining" not in data:
                data["remaining"] = data.get("duration", 3600)
            if "is_running" not in data:
                data["is_running"] = False
            if "expired" not in data:
                data["expired"] = False
            if "last_updated" not in data:
                data["last_updated"] = time.time()

            row_layout = QHBoxLayout()
            row_layout.setContentsMargins(4, 2, 4, 2) # Reduced vertical margins per row[cite: 1]
            row_layout.setSpacing(10)
            
            # Sprite / Icon Label updated to 32x32 dimensions
            lbl_icon = QLabel()
            lbl_icon.setFixedSize(32, 32)
            lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.load_sprite_icon(data, lbl_icon)

            clean_name = data["name"].replace("▶", "").replace("⏸", "").replace("🚨", "").strip()
            lbl_name = QLabel(clean_name)
            lbl_time = QLabel(self.format_time(data["remaining"]))
            lbl_time.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            row_layout.addWidget(lbl_icon, 0)
            row_layout.addWidget(lbl_name, 1)
            row_layout.addWidget(lbl_time, 0)
            
            row_container = TimerRowWidget(idx, self.toggle_row)
            row_container.setLayout(row_layout)
            
            self.container_layout.addWidget(row_container)
            self.row_widgets.append((row_container, lbl_name, lbl_time, lbl_icon))

        if apply_saved_size and "timers_size" in self.main_app.config:
            w, h = self.main_app.config["timers_size"]
            self.resize(w, h)
        else:
            # Adjusted default height scaling to match smaller 32x32 sprite rows[cite: 1]
            self.resize(280, max(60, 16 + (len(self.main_app.timer_rows) * 40)))
        
        if hasattr(self, 'text_hex'):
            self.update_row_styles()

    def format_time(self, seconds):
        if seconds <= 0:
            return "00:00:00"
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    def update_style(self, bg_hex, alpha_value, text_hex, text_alpha, num_hex, num_alpha):
        self.bg_hex = bg_hex
        self.alpha_value = alpha_value
        self.container.set_theme_style(bg_hex, alpha_value)
        self.text_hex, self.text_alpha = text_hex, text_alpha
        self.num_hex, self.num_alpha = num_hex, num_alpha
        self.update_row_styles()

    def update_row_styles(self):
        if not hasattr(self, 'text_hex'): return

        t_col, t_a = QColor(self.text_hex), int((self.text_alpha / 100.0) * 255)
        n_col, n_a = QColor(self.num_hex), int((self.num_alpha / 100.0) * 255)
        
        any_expired = any(r.get("expired", False) for r in self.main_app.timer_rows)
        if any_expired:
            self.container.setStyleSheet("background-color: rgba(230, 60, 60, 45); border-radius: 8px; border: 2px solid rgba(255, 80, 80, 200);")
        else:
            self.container.set_theme_style(self.bg_hex, self.alpha_value)

        for i, (container, lbl_name, lbl_time, lbl_icon) in enumerate(self.row_widgets):
            r = self.main_app.timer_rows[i]
            
            # Refresh icon state / sprite[cite: 1]
            self.load_sprite_icon(r, lbl_icon)

            container.setStyleSheet("background: transparent; border: none;")

            lbl_name.setStyleSheet(f"color: rgba({t_col.red()}, {t_col.green()}, {t_col.blue()}, {t_a}); font-size: 13px; font-weight: bold; border: none; background: transparent;")
            
            if not r.get("is_running", False) or r.get("expired", False):
                lbl_time.setStyleSheet("color: #FF6b6b; font-size: 13px; font-weight: bold; border: none; background: transparent;")
            else:
                lbl_time.setStyleSheet(f"color: rgba({n_col.red()}, {n_col.green()}, {n_col.blue()}, {n_a}); font-size: 13px; font-weight: bold; border: none; background: transparent;")

    def update_row_display(self):
        for i, (_, _, lbl_time, _) in enumerate(self.row_widgets):
            r = self.main_app.timer_rows[i]
            lbl_time.setText(self.format_time(r["remaining"]))
        self.update_row_styles()

    def toggle_row(self, index):
        rows = self.main_app.timer_rows
        if rows and 0 <= index < len(rows):
            self.active_index = index
            r = rows[index]
            if r["remaining"] <= 0:
                r["remaining"] = r.get("duration", 3600)
                r["expired"] = False
            r["is_running"] = not r["is_running"]
            r["last_updated"] = time.time()
            self.save_to_config()
            self.update_row_display()

    def toggle_active(self):
        self.toggle_row(self.active_index)

    def reset_row(self, index):
        rows = self.main_app.timer_rows
        if rows and 0 <= index < len(rows):
            self.active_index = index
            r = rows[index]
            r["is_running"] = False
            r["remaining"] = r.get("duration", 3600)
            r["expired"] = False
            r["last_updated"] = time.time()
            self.save_to_config()
            self.update_row_display()

    def reset_active(self):
        self.reset_row(self.active_index)

    def reset_all(self):
        for r in self.main_app.timer_rows:
            r["is_running"] = False
            r["remaining"] = r.get("duration", 3600)
            r["expired"] = False
            r["last_updated"] = time.time()
        self.save_to_config()
        self.update_row_display()

    def tick_all(self):
        updated = False
        now = time.time()
        for r in self.main_app.timer_rows:
            if r.get("is_running", False) and r["remaining"] > 0:
                delta = int(now - r.get("last_updated", now))
                if delta >= 1:
                    r["remaining"] -= delta
                    r["last_updated"] = now
                    if r["remaining"] <= 0:
                        r["remaining"] = 0
                        r["is_running"] = False
                        r["expired"] = True
                    updated = True
        if updated:
            self.save_to_config()
            self.update_row_display()

    def show_context_menu(self, pos):
        menu = QMenu(self)
        if self.main_app:
            menu.addAction("Toggle Start/Pause Active", self.toggle_active)
            menu.addAction("Reset Active Timer", self.reset_active)
            menu.addAction("Reset All Timers", self.reset_all)
            menu.addSeparator()
            menu.addAction("Toggle Counter", self.main_app.toggle_counter)
            menu.addAction("Toggle Pokedex", self.main_app.toggle_pokedex)
            menu.addAction("Toggle Breeding Calculator", self.main_app.toggle_breeding)
            menu.addAction("Toggle Timers & Reminders", self.main_app.toggle_timers)
            menu.addSeparator()
            menu.addAction("Settings...", self.main_app.open_settings)
        
        if hasattr(self.main_app, "quit_app"):
            menu.addAction("Exit", self.main_app.quit_app)
        else:
            menu.addAction("Exit", QApplication.quit)
        
        menu.exec(pos)