# widgets/timers.py
import time
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QGuiApplication, QFontMetrics
from PyQt6.QtWidgets import QVBoxLayout, QSizeGrip, QMenu, QLabel, QSizePolicy
from core.base_overlay import BaseOverlay, ThemeBackgroundFrame, DisplayRowItem

class TimersWidget(BaseOverlay):
    def __init__(self, main_app):
        super().__init__("Timers & Reminders", main_app)
        self.active_index = 0
        self.row_widgets = []
        
        current_time = time.time()

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

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(2, 2, 2, 2)
        
        self.container = ThemeBackgroundFrame()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(6, 4, 6, 4)
        self.container_layout.setSpacing(2)

        self.layout.addWidget(self.container)

        self.rebuild_rows(apply_saved_size=True)

        if "timers_pos" in self.main_app.config:
            x, y = self.main_app.config["timers_pos"]
            screen = QGuiApplication.primaryScreen()
            if screen:
                screen_geo = screen.availableGeometry()
                x = max(screen_geo.x(), min(x, screen_geo.x() + screen_geo.width() - self.width()))
                y = max(screen_geo.y(), min(y, screen_geo.y() + screen_geo.height() - self.height()))
            self.move(x, y)

        self.size_grip = QSizeGrip(self)
        self.size_grip.setStyleSheet("background: transparent; width: 14px; height: 14px;")

        cfg = getattr(self.main_app, "config", {})
        bg = cfg.get("timers_bg", getattr(self.main_app, "timers_bg", "#1E1E24"))
        opacity = cfg.get("timers_opacity", getattr(self.main_app, "timers_opacity", 90))
        t_color = cfg.get("timers_text_color", getattr(self.main_app, "timers_text_color", "#E2E2E8"))
        t_alpha = cfg.get("timers_text_alpha", getattr(self.main_app, "timers_text_alpha", 100))
        n_color = cfg.get("timers_num_color", getattr(self.main_app, "timers_num_color", "#80A0FF"))
        n_alpha = cfg.get("timers_num_alpha", getattr(self.main_app, "timers_num_alpha", 100))

        self.update_style(bg, opacity, t_color, t_alpha, n_color, n_alpha)

        self.master_timer = QTimer(self)
        self.master_timer.setInterval(1000)
        self.master_timer.timeout.connect(self.tick_all)
        self.master_timer.start()

    def moveEvent(self, event):
        super().moveEvent(event)
        if hasattr(self, "main_app") and hasattr(self.main_app, "config"):
            self.main_app.config["timers_pos"] = [self.x(), self.y()]

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.size_grip.move(self.width() - 20, self.height() - 20)
        if hasattr(self, "main_app") and hasattr(self.main_app, "config"):
            self.main_app.config["timers_size"] = [self.width(), self.height()]

    def closeEvent(self, event):
        if hasattr(self, "master_timer") and self.master_timer.isActive():
            self.master_timer.stop()
        if hasattr(self.main_app, "config"):
            self.main_app.config["timers_pos"] = [self.x(), self.y()]
            self.main_app.config["timers_size"] = [self.width(), self.height()]
        self.save_to_config()
        super().closeEvent(event)

    def save_to_config(self):
        if hasattr(self.main_app, "config"):
            self.main_app.config["timer_rows"] = self.main_app.timer_rows
            if hasattr(self, "bg_hex"):
                self.main_app.config["timers_bg"] = self.bg_hex
            if hasattr(self, "alpha_value"):
                self.main_app.config["timers_opacity"] = self.alpha_value
            if hasattr(self, "text_hex"):
                self.main_app.config["timers_text_color"] = self.text_hex
            if hasattr(self, "text_alpha"):
                self.main_app.config["timers_text_alpha"] = self.text_alpha
            if hasattr(self, "num_hex"):
                self.main_app.config["timers_num_color"] = self.num_hex
            if hasattr(self, "num_alpha"):
                self.main_app.config["timers_num_alpha"] = self.num_alpha

            for save_method in ["save_config", "save_settings", "save", "save_data"]:
                if hasattr(self.main_app, save_method):
                    getattr(self.main_app, save_method)()
                    break

    def _clear_container_layout(self):
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                item.layout().deleteLater()

    def rebuild_rows(self, apply_saved_size=False):
        self._clear_container_layout()
        self.row_widgets.clear()

        row_count = len(self.main_app.timer_rows)
        min_h = max(70, 16 + (row_count * 30))
        min_w = 210
        self.setMinimumSize(min_w, min_h)

        for idx, data in enumerate(self.main_app.timer_rows):
            data.setdefault("remaining", data.get("duration", 3600))
            data.setdefault("is_running", False)
            data.setdefault("expired", False)
            data.setdefault("last_updated", time.time())

            row_item = DisplayRowItem(idx, icon_size=24, on_click=None)
            self.container_layout.addWidget(row_item)
            self.row_widgets.append(row_item)

        if apply_saved_size and "timers_size" in self.main_app.config:
            saved_w, saved_h = self.main_app.config["timers_size"]
            self.resize(max(min_w, saved_w), max(min_h, saved_h))
        else:
            self.resize(min_w, min_h)
        
        if hasattr(self, 'text_hex'):
            self.update_row_styles()

    def format_time(self, seconds):
        if seconds <= 0: return "00:00:00"
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    def update_style(self, bg_hex, alpha_value, text_hex, text_alpha, num_hex, num_alpha):
        self.bg_hex = bg_hex
        self.alpha_value = alpha_value
        self.text_hex = text_hex
        self.text_alpha = text_alpha
        self.num_hex = num_hex
        self.num_alpha = num_alpha

        if hasattr(self.main_app, "config"):
            self.main_app.config["timers_bg"] = bg_hex
            self.main_app.config["timers_opacity"] = alpha_value
            self.main_app.config["timers_text_color"] = text_hex
            self.main_app.config["timers_text_alpha"] = text_alpha
            self.main_app.config["timers_num_color"] = num_hex
            self.main_app.config["timers_num_alpha"] = num_alpha

        setattr(self.main_app, "timers_bg", bg_hex)
        setattr(self.main_app, "timers_opacity", alpha_value)
        setattr(self.main_app, "timers_text_color", text_hex)
        setattr(self.main_app, "timers_text_alpha", text_alpha)
        setattr(self.main_app, "timers_num_color", num_hex)
        setattr(self.main_app, "timers_num_alpha", num_alpha)

        self.container.set_theme_style(bg_hex, alpha_value)
        self.update_row_styles()
        self.save_to_config()

    def update_row_styles(self):
        if not hasattr(self, 'text_hex'): return

        any_expired = any(r.get("expired", False) for r in self.main_app.timer_rows)
        if any_expired:
            self.container.setStyleSheet("background-color: rgba(230, 60, 60, 45); border-radius: 8px; border: 2px solid rgba(255, 80, 80, 200);")
        else:
            self.container.set_theme_style(self.bg_hex, self.alpha_value)

        for i, row in enumerate(self.row_widgets):
            if i >= len(self.main_app.timer_rows): break
            r = self.main_app.timer_rows[i]
            
            row.load_sprite(r, cache_prefix="timer_sprite")
            row.setStyleSheet("background: transparent; border: none;")

            clean_name = r["name"].replace("▶", "").replace("⏸", "").replace("🚨", "").strip()
            time_str = self.format_time(r["remaining"])
            
            val_color = "#FF6b6b" if (not r.get("is_running", False) or r.get("expired", False)) else None

            style_config = {
                "text_hex": self.text_hex,
                "text_alpha": self.text_alpha,
                "num_hex": self.num_hex,
                "num_alpha": self.num_alpha,
                "weight": "bold",
                "value_color": val_color
            }
            row.update_row_content(clean_name, time_str, style_config)

            row_lay = row.layout
            if row_lay and hasattr(row_lay, "setSpacing"):
                row_lay.setContentsMargins(2, 0, 2, 0)
                row_lay.setSpacing(8)

            labels = row.findChildren(QLabel)
            if labels:
                name_lbl = getattr(row, "name_label", None) or getattr(row, "title_label", None)
                val_lbl = getattr(row, "value_label", None) or getattr(row, "time_label", None)

                if not name_lbl and len(labels) >= 2:
                    name_lbl = labels[0]
                if not val_lbl and len(labels) >= 1:
                    val_lbl = labels[-1]

                if name_lbl:
                    name_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                    name_lbl.setMinimumWidth(40)

                if val_lbl:
                    val_lbl.setCursor(Qt.CursorShape.PointingHandCursor)
                    fm = QFontMetrics(val_lbl.font())
                    needed_w = fm.horizontalAdvance("00:00:00") + 6
                    val_lbl.setMinimumWidth(needed_w)
                    val_lbl.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
                    val_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    idx = i
                    val_lbl.mousePressEvent = lambda event, index=idx: self.toggle_row(index)

    def update_row_display(self):
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
                last_up = r.get("last_updated", now)
                elapsed = now - last_up
                if elapsed >= 1.0:
                    r["remaining"] -= 1
                    r["last_updated"] = last_up + 1.0
                    if r["remaining"] <= 0:
                        r["remaining"] = 0
                        r["is_running"] = False
                        r["expired"] = True
                    updated = True
        if updated:
            if hasattr(self.main_app, "config"):
                self.main_app.config["timer_rows"] = self.main_app.timer_rows
            self.update_row_display()

    def show_context_menu(self, pos):
        menu = QMenu(self)
        menu.addAction("Toggle Start/Pause Active", self.toggle_active)
        menu.addAction("Reset Active Timer", self.reset_active)
        menu.addAction("Reset All Timers", self.reset_all)
        menu.addSeparator()
        self.populate_base_actions(menu)
        menu.exec(pos)