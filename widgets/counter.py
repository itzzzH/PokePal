# widgets/counter.py
import os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPixmap
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QSizeGrip
from core.base_overlay import BaseOverlay, ThemeBackgroundFrame, InteractiveRowWidget
from core.utils import clean_count

class CounterWidget(BaseOverlay):
    def __init__(self, main_app):
        super().__init__("Counter", main_app)
        self.active_index = 0
        
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

        if "counter_pos" in self.main_app.config:
            x, y = self.main_app.config["counter_pos"]
            self.move(x, y)

        self.size_grip = QSizeGrip(self)
        self.size_grip.setStyleSheet("background: transparent; width: 14px; height: 14px;")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.size_grip.move(self.width() - 20, self.height() - 20)

    def load_sprite_icon(self, data, lbl_icon):
        """Loads a smaller sprite pixmap (28x28) from data/sprites or data/sprites/items with no box/highlight."""
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
                    # Reduced sprite size from 40x40 to 28x28[cite: 2]
                    lbl_icon.setPixmap(pixmap.scaled(28, 28, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                    lbl_icon.setStyleSheet("border: none; background: transparent;")
                    return

        lbl_icon.clear()
        lbl_icon.setStyleSheet("border: none; background: transparent;")

    def rebuild_rows(self, apply_saved_size=False):
        for i in reversed(range(self.container_layout.count())):
            item = self.container_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)

        self.row_widgets = []
        for idx, data in enumerate(self.main_app.counter_rows):
            data["count"] = clean_count(data["count"])
            if "sprite_folder" not in data:
                data["sprite_folder"] = "pokemon"
            if "sprite_id" not in data:
                data["sprite_id"] = ""

            row_layout = QHBoxLayout()
            row_layout.setContentsMargins(4, 2, 4, 2)
            row_layout.setSpacing(8)
            
            # Label size updated to 28x28
            lbl_icon = QLabel()
            lbl_icon.setFixedSize(28, 28)
            lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_icon.setStyleSheet("border: none; background: transparent;")
            self.load_sprite_icon(data, lbl_icon)

            clean_name = data["name"].replace("▶", "").strip()
            lbl_name = QLabel(clean_name)
            lbl_count = QLabel(str(data["count"]))
            lbl_count.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            
            row_layout.addWidget(lbl_icon, 0)
            row_layout.addWidget(lbl_name, 1)
            row_layout.addWidget(lbl_count, 0)
            
            row_container = InteractiveRowWidget(idx, self.handle_counter_wheel_event)
            row_container.setLayout(row_layout)
            
            self.container_layout.addWidget(row_container)
            self.row_widgets.append((row_container, lbl_name, lbl_count, lbl_icon))

        if apply_saved_size and "counter_size" in self.main_app.config:
            w, h = self.main_app.config["counter_size"]
            self.resize(w, h)
        else:
            # Adjusted default height calculation for smaller 28x28 counter rows[cite: 2]
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

        t_col, t_a = QColor(self.text_hex), int((self.text_alpha / 100.0) * 255)
        n_col, n_a = QColor(self.num_hex), int((self.num_alpha / 100.0) * 255)
        
        for i, (container, lbl_name, lbl_count, lbl_icon) in enumerate(self.row_widgets):
            r = self.main_app.counter_rows[i]
            self.load_sprite_icon(r, lbl_icon)

            is_active = (i == self.active_index)
            weight = "bold" if is_active else "normal"
            
            clean_name = r["name"].replace("▶", "").strip()
            display_name = f"▶ {clean_name}" if is_active else clean_name
            lbl_name.setText(display_name)

            if is_active:
                container.setStyleSheet("background-color: rgba(128, 160, 255, 35); border-radius: 6px; border: 1px solid rgba(128, 160, 255, 120);")
            else:
                container.setStyleSheet("background: transparent; border: none;")

            lbl_name.setStyleSheet(f"color: rgba({t_col.red()}, {t_col.green()}, {t_col.blue()}, {t_a}); font-size: 13px; font-weight: {weight}; border: none; background: transparent;")
            lbl_count.setStyleSheet(f"color: rgba({n_col.red()}, {n_col.green()}, {n_col.blue()}, {n_a}); font-size: 13px; font-weight: {weight}; border: none; background: transparent;")

    def update_row_display(self):
        for i, (_, lbl_name, lbl_count, _) in enumerate(self.row_widgets):
            c_val = clean_count(self.main_app.counter_rows[i]["count"])
            self.main_app.counter_rows[i]["count"] = c_val
            lbl_count.setText(str(c_val))
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