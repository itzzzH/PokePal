# widgets/counter.py
from PyQt6.QtWidgets import QVBoxLayout, QSizeGrip
from core.base_overlay import BaseOverlay, ThemeBackgroundFrame, DisplayRowItem
from core.utils import clean_count

class CounterWidget(BaseOverlay):
    def __init__(self, main_app):
        super().__init__("Counter", main_app)
        self.active_index = 0
        self.row_widgets = []
        
        if hasattr(self.main_app, "counter_rows"):
            for r in self.main_app.counter_rows:
                if "sprite_folder" not in r:
                    r["sprite_folder"] = "pokemon"
                if "sprite_id" not in r:
                    r["sprite_id"] = ""

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(4, 4, 4, 4)
        
        self.container = ThemeBackgroundFrame()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(8, 6, 8, 6)
        self.container_layout.setSpacing(2)

        self.layout.addWidget(self.container)
        self.rebuild_rows(apply_saved_size=True)

        self.apply_initial_position("counter_pos", default_rel_x=0.05, default_rel_y=0.10)

        self.size_grip = QSizeGrip(self)
        self.size_grip.setStyleSheet("background: transparent; width: 14px; height: 14px;")

    def moveEvent(self, event):
        super().moveEvent(event)
        if hasattr(self, "main_app") and hasattr(self.main_app, "config"):
            self.main_app.config["counter_pos"] = (self.x(), self.y())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.size_grip.move(self.width() - 20, self.height() - 20)
        if hasattr(self, "main_app") and hasattr(self.main_app, "config"):
            self.main_app.config["counter_size"] = (self.width(), self.height())

    def closeEvent(self, event):
        if hasattr(self, "main_app") and hasattr(self.main_app, "save_settings"):
            self.main_app.save_settings()
        super().closeEvent(event)

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

        for idx, data in enumerate(self.main_app.counter_rows):
            data["count"] = clean_count(data["count"])
            data.setdefault("sprite_folder", "pokemon")
            data.setdefault("sprite_id", "")

            row_item = DisplayRowItem(idx, icon_size=28, on_wheel=self.handle_counter_wheel_event)
            self.container_layout.addWidget(row_item)
            self.row_widgets.append(row_item)

        if apply_saved_size and "counter_size" in self.main_app.config:
            w, h = self.main_app.config["counter_size"]
            self.resize(w, h)
        else:
            self.resize(280, max(60, 16 + (len(self.main_app.counter_rows) * 34)))
        self.update_row_styles()

    def handle_counter_wheel_event(self, event, index):
        self.active_index = index
        self.update_row_styles()
        if event.angleDelta().y() > 0:
            self.increment_active()
        elif event.angleDelta().y() < 0:
            self.decrement_active()

    def update_style(self, bg_hex, alpha_value, text_hex, text_alpha, num_hex, num_alpha):
        self.container.set_theme_style(bg_hex, alpha_value)
        self.text_hex, self.text_alpha = text_hex, text_alpha
        self.num_hex, self.num_alpha = num_hex, num_alpha
        self.update_row_styles()

    def update_row_styles(self):
        if not hasattr(self, 'text_hex'): return

        for i, row in enumerate(self.row_widgets):
            if i >= len(self.main_app.counter_rows): break
            r = self.main_app.counter_rows[i]
            row.load_sprite(r, cache_prefix="counter_sprite")

            is_active = (i == self.active_index)
            clean_name = r["name"].replace("▶", "").strip()
            display_name = f"▶ {clean_name}" if is_active else clean_name

            row.setStyleSheet("background: transparent; border: none;")

            style_config = {
                "text_hex": self.text_hex,
                "text_alpha": self.text_alpha,
                "num_hex": self.num_hex,
                "num_alpha": self.num_alpha,
                "weight": "bold" if is_active else "normal"
            }
            row.update_row_content(display_name, str(r["count"]), style_config)

    def update_row_display(self):
        for i, row in enumerate(self.row_widgets):
            if i < len(self.main_app.counter_rows):
                c_val = clean_count(self.main_app.counter_rows[i]["count"])
                self.main_app.counter_rows[i]["count"] = c_val
        self.update_row_styles()

    def increment_active(self):
        rows = self.main_app.counter_rows
        if rows and 0 <= self.active_index < len(rows):
            rows[self.active_index]["count"] = clean_count(rows[self.active_index]["count"]) + 1
            self.update_row_display()

    def decrement_active(self):
        rows = self.main_app.counter_rows
        if rows and 0 <= self.active_index < len(rows):
            curr = clean_count(rows[self.active_index]["count"])
            if curr > 0:
                rows[self.active_index]["count"] = curr - 1
                self.update_row_display()

    def reset_all(self):
        for row in self.main_app.counter_rows:
            row["count"] = 0
        self.update_row_display()