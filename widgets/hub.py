from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPixmap, QColor
from core.base_overlay import BaseOverlay

class PokeballHub(BaseOverlay):
    def __init__(self, main_app):
        super().__init__("Hub", main_app)
        self.setFixedSize(60, 60)

        if "hub_pos" in self.main_app.config:
            x, y = self.main_app.config["hub_pos"]
            self.move(x, y)

        self.raw_pixmap = None
        
        for path in [Path("data") / "ball.png", Path("ball.png")]:
            if path.exists():
                self.raw_pixmap = QPixmap(str(path))
                break

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setOpacity(self.main_app.hub_opacity / 100.0)

        if self.raw_pixmap and not self.raw_pixmap.isNull():
            scaled_pix = self.raw_pixmap.scaled(
                60, 60, 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            painter.drawPixmap(0, 0, scaled_pix)
        else:
            painter.setBrush(QColor(0, 0, 0, 90))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(5, 5, 50, 50)

    def update_style(self):
        self.update()