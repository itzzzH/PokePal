# core/base_overlay.py
import os
import webbrowser
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QColor, QPixmap, QPixmapCache
from PyQt6.QtWidgets import QWidget, QFrame, QHBoxLayout, QLabel, QMenu, QApplication

class BaseOverlay(QWidget):
    """Base class for frameless overlay widgets."""
    def __init__(self, title, main_app):
        super().__init__()
        self.title = title
        self.main_app = main_app
        self.drag_position = QPoint()

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            window = self.windowHandle()
            if window is not None:
                window.startSystemMove()
            else:
                self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def contextMenuEvent(self, event):
        pos = event.globalPosition().toPoint() if hasattr(event, "globalPosition") else event.globalPos()
        self.show_context_menu(pos)

    def populate_base_actions(self, menu):
        """Populates shared app navigation and settings options into a menu."""
        
        # Check if an update is available and displays in context menu
        if getattr(self.main_app, "update_available", False):
            menu.addSeparator()
            update_action = menu.addAction("✨ Update Available! (Click to open)")
            update_action.triggered.connect(
                lambda: webbrowser.open(self.main_app.latest_version_url)
            )
            menu.addSeparator()

        if self.main_app:
            toggles = [
                ("Toggle Counter", getattr(self.main_app, "toggle_counter", None)),
                ("Toggle Timers", getattr(self.main_app, "toggle_timers", None)),
                ("Toggle Notes", getattr(self.main_app, "toggle_notepad", None) or getattr(self.main_app, "toggle_notes", None)),
                ("Toggle Pokédex", getattr(self.main_app, "toggle_pokedex", None)),
                ("Toggle Locations", getattr(self.main_app, "toggle_locations", None)),
                ("Toggle Breeding Calculator", getattr(self.main_app, "toggle_breeding", None)),
                ("Toggle Matchup Calculator", getattr(self.main_app, "toggle_weakness", None) or getattr(self.main_app, "toggle_matchup", None)),
            ]

            for label, action in toggles:
                if action:
                    menu.addAction(label, action)

            menu.addSeparator()
            if hasattr(self.main_app, "open_settings"):
                menu.addAction("Settings...", self.main_app.open_settings)

        if hasattr(self.main_app, "quit_app"):
            menu.addAction("Exit", self.main_app.quit_app)
        else:
            menu.addAction("Exit", QApplication.quit)

    def show_context_menu(self, pos):
        """Default context menu for overlays displaying shared app controls."""
        menu = QMenu(self)
        self.populate_base_actions(menu)
        menu.exec(pos)

class ThemeBackgroundFrame(QFrame):
    """Container frame supporting dynamic background color and alpha opacity."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_theme_style("#1E1E24", 90)

    def set_theme_style(self, bg_hex, alpha_value):
        col = QColor(bg_hex)
        alpha = int((alpha_value / 100.0) * 255)
        self.setStyleSheet(
            f"ThemeBackgroundFrame {{ "
            f"background-color: rgba({col.red()}, {col.green()}, {col.blue()}, {alpha}); "
            f"border-radius: 10px; "
            f"border: 1px solid rgba(255, 255, 255, 30); "
            f"}}"
        )

class InteractiveRowWidget(QFrame):
    """Legacy row frame retained for backwards compatibility."""
    def __init__(self, index, wheel_callback=None, parent=None):
        super().__init__(parent)
        self.index = index
        self.wheel_callback = wheel_callback

    def wheelEvent(self, event):
        if self.wheel_callback:
            self.wheel_callback(event, self.index)
        super().wheelEvent(event)

class DisplayRowItem(QFrame):
    """Consolidated component for displaying list rows with sprite icons, title labels, and value displays."""
    def __init__(self, index, icon_size=28, on_click=None, on_wheel=None, parent=None):
        super().__init__(parent)
        self.index = index
        self.icon_size = icon_size
        self.on_click = on_click
        self.on_wheel = on_wheel

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(4, 2, 4, 2)
        self.layout.setSpacing(8)

        self.lbl_icon = QLabel()
        self.lbl_icon.setFixedSize(self.icon_size, self.icon_size)
        self.lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_icon.setStyleSheet("border: none; background: transparent;")

        self.lbl_name = QLabel()
        self.lbl_value = QLabel()
        self.lbl_value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.layout.addWidget(self.lbl_icon, 0)
        self.layout.addWidget(self.lbl_name, 1)
        self.layout.addWidget(self.lbl_value, 0)

    def mousePressEvent(self, event):
        if self.on_click and event.button() == Qt.MouseButton.LeftButton:
            self.on_click(self.index)
        super().mousePressEvent(event)

    def wheelEvent(self, event):
        if self.on_wheel:
            self.on_wheel(event, self.index)
        super().wheelEvent(event)

    def load_sprite(self, data, cache_prefix="row_sprite"):
        folder = data.get("sprite_folder", "pokemon")
        sprite_id = str(data.get("sprite_id", "")).strip()

        if sprite_id:
            sub_folder = "items" if folder == "items" else ""
            cache_key = f"{cache_prefix}_{sub_folder}_{sprite_id}"
            pixmap = QPixmapCache.find(cache_key)

            if pixmap is None:
                path = os.path.join("data", "sprites", sub_folder, f"{sprite_id}.png") if sub_folder else os.path.join("data", "sprites", f"{sprite_id}.png")
                if os.path.exists(path):
                    loaded_pixmap = QPixmap(path)
                    if not loaded_pixmap.isNull():
                        pixmap = loaded_pixmap.scaled(self.icon_size, self.icon_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                        QPixmapCache.insert(cache_key, pixmap)

            if pixmap and not pixmap.isNull():
                self.lbl_icon.setPixmap(pixmap)
                self.lbl_icon.setStyleSheet("border: none; background: transparent;")
                return

        if data.get("expired", False):
            self.lbl_icon.setText("🚨")
        elif data.get("is_running", False):
            self.lbl_icon.setText("⏸")
        elif "is_running" in data:
            self.lbl_icon.setText("▶")
        else:
            self.lbl_icon.clear()
        self.lbl_icon.setStyleSheet("font-size: 16px; border: none; background: transparent;")

    def update_row_content(self, name_text, value_text, style_config):
        self.lbl_name.setText(name_text)
        self.lbl_value.setText(value_text)

        t_col = QColor(style_config.get("text_hex", "#E2E2E8"))
        t_a = int((style_config.get("text_alpha", 100) / 100.0) * 255)
        n_col = QColor(style_config.get("num_hex", "#80A0FF"))
        n_a = int((style_config.get("num_alpha", 100) / 100.0) * 255)
        weight = style_config.get("weight", "normal")
        value_color_override = style_config.get("value_color")

        self.lbl_name.setStyleSheet(
            f"color: rgba({t_col.red()}, {t_col.green()}, {t_col.blue()}, {t_a}); "
            f"font-size: 13px; font-weight: {weight}; border: none; background: transparent;"
        )

        val_style = value_color_override or f"rgba({n_col.red()}, {n_col.green()}, {n_col.blue()}, {n_a})"
        self.lbl_value.setStyleSheet(
            f"color: {val_style}; "
            f"font-size: 13px; font-weight: {weight}; border: none; background: transparent;"
        )