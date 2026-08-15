import os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPixmap, QColor, QAction
from PyQt6.QtWidgets import QMenu
from core.base_overlay import BaseOverlay

class PokeballHub(BaseOverlay):
    def __init__(self, main_app):
        super().__init__("Hub", main_app)
        self.setFixedSize(60, 60)

        if "hub_pos" in self.main_app.config:
            x, y = self.main_app.config["hub_pos"]
            self.move(x, y)

        self.raw_pixmap = None
        
        paths = [os.path.join("data", "ball.png"), "ball.png"]
        for p in paths:
            if os.path.exists(p):
                self.raw_pixmap = QPixmap(p)
                break

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setOpacity(self.main_app.hub_opacity / 100.0)

        if self.raw_pixmap and not self.raw_pixmap.isNull():
            scaled_pix = self.raw_pixmap.scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            painter.drawPixmap(0, 0, scaled_pix)
        else:
            painter.setBrush(QColor(0, 0, 0, 90))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(5, 5, 50, 50)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1E1E24;
                color: #E2E2E8;
                border: 1px solid #363644;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #3B82F6;
                color: #FFFFFF;
            }
        """)

        action_weakness = QAction("Toggle Matchup Calculator", self)
        action_weakness.triggered.connect(self.main_app.toggle_weakness)
        menu.addAction(action_weakness)

        action_notepad = QAction("Toggle Notes", self)
        action_notepad.triggered.connect(self.main_app.toggle_notepad)
        menu.addAction(action_notepad)

        menu.addSeparator()

        action_counter = QAction("Toggle Counter", self)
        action_counter.triggered.connect(self.main_app.toggle_counter)
        menu.addAction(action_counter)

        action_pokedex = QAction("Toggle Pokedex", self)
        action_pokedex.triggered.connect(self.main_app.toggle_pokedex)
        menu.addAction(action_pokedex)

        action_breeding = QAction("Toggle Breeding Calculator", self)
        action_breeding.triggered.connect(self.main_app.toggle_breeding)
        menu.addAction(action_breeding)

        action_timers = QAction("Toggle Timers", self)
        action_timers.triggered.connect(self.main_app.toggle_timers)
        menu.addAction(action_timers)

        menu.addSeparator()

        action_settings = QAction("Settings", self)
        action_settings.triggered.connect(self.main_app.open_settings)
        menu.addAction(action_settings)

        menu.addSeparator()

        action_quit = QAction("Quit PokePal", self)
        action_quit.triggered.connect(self.main_app.quit_app)
        menu.addAction(action_quit)

        # PyQt6 compatible context menu execution position
        menu.exec(event.globalPosition().toPoint())

    def update_style(self):
        self.update()