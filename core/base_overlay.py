# core/base_overlay.py
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QWidget, QFrame, QMenu, QApplication

class ThemeBackgroundFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.bg_color_hex = "#1E1E24"
        self.alpha_val = 85

    def set_theme_style(self, color_hex, alpha_val):
        self.bg_color_hex = color_hex
        self.alpha_val = alpha_val
        col = QColor(color_hex)
        alpha_byte = int((alpha_val / 100.0) * 255)
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: rgba({col.red()}, {col.green()}, {col.blue()}, {alpha_byte});
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, {min(alpha_byte, 35)});
            }}
        """)

class InteractiveRowWidget(QWidget):
    def __init__(self, index, scroll_callback):
        super().__init__()
        self.index = index
        self.scroll_callback = scroll_callback
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def wheelEvent(self, event):
        if self.scroll_callback:
            self.scroll_callback(event, self.index)
        event.accept()

class BaseOverlay(QWidget):
    def __init__(self, title, main_app=None):
        super().__init__()
        self.main_app = main_app
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.drag_offset = QPoint()
        self.title = title
        self.dragging = False

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_offset = event.position().toPoint()
            self.dragging = False
        elif event.button() == Qt.MouseButton.RightButton:
            self.show_context_menu(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_offset)
            self.dragging = True

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.dragging:
            if self.main_app:
                self.main_app.save_settings()

    def show_context_menu(self, pos):
        menu = QMenu(self)
        if self.main_app:
            menu.addAction("Toggle Counter", self.main_app.toggle_counter)
            menu.addAction("Toggle Pokedex", self.main_app.toggle_pokedex)
            menu.addAction("Toggle Breeding Calculator", self.main_app.toggle_breeding)
            menu.addAction("Toggle Timers", self.main_app.toggle_timers)
            menu.addAction("Toggle Matchup Calculator", self.main_app.toggle_weakness)
            menu.addAction("Toggle Notes", self.main_app.toggle_notepad)  # <--- Added sticky note action
            menu.addSeparator()
            menu.addAction("Settings...", self.main_app.open_settings)
        menu.addAction("Exit", QApplication.quit)
        menu.exec(pos)