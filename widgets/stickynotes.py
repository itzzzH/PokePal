# widgets/stickynotes.py
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QVBoxLayout, QLabel, QTextEdit, 
    QFrame, QSizeGrip
)
from core.base_overlay import BaseOverlay

class NotepadWidget(BaseOverlay):
    def __init__(self, main_app):
        super().__init__("Sticky Note", main_app)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(4, 4, 4, 4)
        
        self.container = QFrame()
        self.container.setStyleSheet("""
            QFrame {
                background-color: #1A1A20;
                border-radius: 12px;
                border: 1px solid #323242;
            }
        """)
        
        self.c_layout = QVBoxLayout(self.container)
        self.c_layout.setContentsMargins(10, 10, 10, 10)
        self.c_layout.setSpacing(8)
        
        # Header
        header_lbl = QLabel("📝 Notes")
        header_lbl.setStyleSheet("color: #FFFFFF; font-size: 13px; font-weight: bold; border: none; background: transparent;")
        self.c_layout.addWidget(header_lbl)

        # Text Editor
        self.text_edit = QTextEdit()
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #22222E;
                color: #C0C0D0;
                border: 1px solid #3E3E50;
                border-radius: 6px;
                font-size: 11px;
                padding: 6px;
            }
        """)
        
        # Load saved notes if available in config
        saved_text = self.main_app.config.get("sticky_note_text", "")
        self.text_edit.setPlainText(saved_text)
        self.text_edit.textChanged.connect(self.save_notes)
        
        self.c_layout.addWidget(self.text_edit, 1)
        self.layout.addWidget(self.container)

        if "sticky_note_pos" in self.main_app.config:
            x, y = self.main_app.config["sticky_note_pos"]
            self.move(x, y)
        if "sticky_note_size" in self.main_app.config:
            w, h = self.main_app.config["sticky_note_size"]
            self.resize(w, h)
        else:
            self.resize(300, 300)

        self.size_grip = QSizeGrip(self)
        self.size_grip.setStyleSheet("background: transparent; width: 14px; height: 14px;")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.size_grip.move(self.width() - 20, self.height() - 20)

    def save_notes(self):
        self.main_app.config["sticky_note_text"] = self.text_edit.toPlainText()
        if hasattr(self.main_app, "save_config"):
            self.main_app.save_config()