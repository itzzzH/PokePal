# widgets/stickynotes.py
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, 
    QFrame, QSizeGrip, QTabWidget, QPushButton,
    QMessageBox, QMenu, QInputDialog, QTabBar, QApplication, QFileDialog
)
from core.base_overlay import BaseOverlay
import os

class NotepadWidget(BaseOverlay):
    def __init__(self, main_app):
        super().__init__("Sticky Note", main_app)

        # Debounce timer to batch disk saves and eliminate typing stutter
        self.save_timer = QTimer(self)
        self.save_timer.setSingleShot(True)
        self.save_timer.setInterval(800)
        self.save_timer.timeout.connect(self.save_notes)

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
        
        # Header Layout (Notes title on left, Add button on right)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        header_lbl = QLabel("📝 Notes")
        header_lbl.setStyleSheet("""
            color: rgba(255, 255, 255, 128); 
            font-size: 13px; 
            font-weight: bold; 
            border: none; 
            background: transparent;
        """)
        header_layout.addWidget(header_lbl)
        header_layout.addStretch()

        # Add Tab Button (In line with header)
        self.add_btn = QPushButton("+")
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_btn.setFixedSize(24, 24)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #888899; 
                font-family: Arial, sans-serif;
                font-size: 15px; 
                font-weight: bold; 
                border: none;
                border-radius: 4px;
                padding: 0px;
                margin: 0px;
            }
            QPushButton:hover { 
                background-color: #22222E;
                color: #FFFFFF; 
            }
        """)
        self.add_btn.clicked.connect(self.add_new_tab)
        header_layout.addWidget(self.add_btn)
        
        self.c_layout.addLayout(header_layout)

        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #3E3E50;
                border-radius: 6px;
                background-color: #22222E;
            }
            QTabBar::tab {
                background-color: #1A1A20;
                color: #888899;
                padding: 6px 10px;
                border: 1px solid #3E3E50;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #22222E;
                color: #FFFFFF;
                border-bottom-color: #22222E;
            }
        """)

        # Load saved notes from config or create a default tab
        saved_tabs = self.main_app.config.get("sticky_note_tabs", [{"title": "Note 1", "text": ""}])
        
        # Migrate old single-note data if it exists and no tabs are saved
        if "sticky_note_tabs" not in self.main_app.config and "sticky_note_text" in self.main_app.config:
            old_text = self.main_app.config.get("sticky_note_text", "")
            saved_tabs = [{"title": "Note 1", "text": old_text}]
            
        for tab_data in saved_tabs:
            self.add_tab(tab_data.get("title", "Note"), tab_data.get("text", ""))
        
        self.c_layout.addWidget(self.tabs, 1)
        self.layout.addWidget(self.container)

        # Set minimum size to prevent widget collapse on lower resolution screens
        self.setMinimumSize(220, 180)

        # Restore saved dimensions or default size
        w, h = 300, 300
        if "sticky_note_size" in self.main_app.config:
            saved_w, saved_h = self.main_app.config["sticky_note_size"]
            w, h = max(220, saved_w), max(180, saved_h)
        self.resize(w, h)

        # Restore saved position while clamping within screen boundaries for variable display resolutions
        if "sticky_note_pos" in self.main_app.config:
            x, y = self.main_app.config["sticky_note_pos"]
            screen = QGuiApplication.primaryScreen()
            if screen:
                screen_geo = screen.availableGeometry()
                x = max(screen_geo.x(), min(x, screen_geo.x() + screen_geo.width() - w))
                y = max(screen_geo.y(), min(y, screen_geo.y() + screen_geo.height() - h))
            self.move(x, y)

        self.size_grip = QSizeGrip(self)
        self.size_grip.setStyleSheet("background: transparent; width: 14px; height: 14px;")
        
        self.update_tab_close_buttons()

    def schedule_save(self):
        """Schedules a delayed save to avoid synchronous file operations on every key press."""
        self.save_timer.start(800)

    def update_tab_close_buttons(self):
        # Hide the close button if only 1 tab is present
        if self.tabs.count() == 1:
            self.tabs.tabBar().setTabButton(0, QTabBar.ButtonPosition.RightSide, None)

    def add_new_tab(self):
        tab_count = self.tabs.count() + 1
        self.add_tab(f"Note {tab_count}", "")
        self.tabs.setCurrentIndex(self.tabs.count() - 1)
        self.update_tab_close_buttons()
        self.save_notes()

    def add_tab(self, title, text):
        text_edit = QTextEdit()
        text_edit.setAcceptRichText(False)  # Disables rich text insertion/formatting support
        text_edit.setPlainText(text if text else "")  # Treats content strictly as plain text
        text_edit.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                color: #C0C0D0;
                border: none;
                font-size: 11px;
                padding: 6px;
            }
        """)
        text_edit.textChanged.connect(self.schedule_save)
        
        self.tabs.addTab(text_edit, title)
        self.update_tab_close_buttons()

    def close_tab(self, index):
        if self.tabs.count() <= 1:
            return
            
        text_widget = self.tabs.widget(index)
        content = text_widget.toPlainText().strip()
        
        if content:
            reply = QMessageBox.question(
                self,
                "Close Tab",
                "This note contains text. Are you sure you want to close it and lose your changes?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return
                
        self.tabs.removeTab(index)
        self.update_tab_close_buttons()
        self.save_notes()

    def rename_tab(self, index):
        current_title = self.tabs.tabText(index)
        new_title, ok = QInputDialog.getText(
            self, 
            "Rename Tab", 
            "Enter new tab name:", 
            text=current_title
        )
        if ok and new_title.strip():
            self.tabs.setTabText(index, new_title.strip())
            self.save_notes()

    def save_note_as_txt(self, index):
        """Opens a file dialog to save the contents of the selected note tab as a text file."""
        if index == -1:
            return
        title = self.tabs.tabText(index)
        text_widget = self.tabs.widget(index)
        content = text_widget.toPlainText()  # Exports pure plain text
        
        default_filename = "".join(c for c in title if c.isalnum() or c in (' ', '_', '-')).strip() + ".txt"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Note as Text File",
            default_filename,
            "Text Files (*.txt)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save file:\n{e}")

    def load_note_from_txt(self):
        """Opens a file dialog to load a text file into a new note tab."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Note File",
            "",
            "Text Files (*.txt)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                self.add_tab(base_name if base_name else "Imported Note", content)
                self.tabs.setCurrentIndex(self.tabs.count() - 1)
                self.update_tab_close_buttons()
                self.save_notes()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load file:\n{e}")

    def moveEvent(self, event):
        super().moveEvent(event)
        if hasattr(self, "main_app") and hasattr(self.main_app, "config"):
            self.main_app.config["sticky_note_pos"] = [self.x(), self.y()]

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.size_grip.move(self.width() - 20, self.height() - 20)
        if hasattr(self, "main_app") and hasattr(self.main_app, "config"):
            self.main_app.config["sticky_note_size"] = [self.width(), self.height()]

    def closeEvent(self, event):
        """Ensures notes, position, and window dimensions are fully persisted on exit."""
        if hasattr(self, "save_timer") and self.save_timer.isActive():
            self.save_timer.stop()
        self.save_notes()
        if self.main_app:
            self.main_app.config["sticky_note_pos"] = [self.x(), self.y()]
            self.main_app.config["sticky_note_size"] = [self.width(), self.height()]
            if hasattr(self.main_app, "save_settings"):
                self.main_app.save_settings()
        super().closeEvent(event)

    def save_notes(self):
        """Helper method to sync notes into config using the controller's save_settings method."""
        if hasattr(self, "save_timer") and self.save_timer.isActive():
            self.save_timer.stop()

        if hasattr(self.main_app, "config"):
            tabs_data = []
            for i in range(self.tabs.count()):
                title = self.tabs.tabText(i)
                text_widget = self.tabs.widget(i)
                tabs_data.append({"title": title, "text": text_widget.toPlainText()})  # Persists plain text string
                
            self.main_app.config["sticky_note_tabs"] = tabs_data
            
            if hasattr(self.main_app, "save_settings"):
                self.main_app.save_settings()

    def show_context_menu(self, global_pos):
        """Overrides BaseOverlay.show_context_menu to add sticky-note specific options alongside global ones."""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1A1A20;
                color: #FFFFFF;
                border: 1px solid #3E3E50;
            }
            QMenu::item:selected {
                background-color: #3E3E50;
            }
        """)
        
        tab_bar = self.tabs.tabBar()
        local_tab_pos = tab_bar.mapFromGlobal(global_pos)
        target_index = -1
        
        if tab_bar.rect().contains(local_tab_pos):
            target_index = tab_bar.tabAt(local_tab_pos)
            
        if target_index == -1:
            target_index = self.tabs.currentIndex()

        if target_index != -1:
            current_title = self.tabs.tabText(target_index)
            menu.addAction(f"✏️ Rename Tab ('{current_title}')", lambda idx=target_index: self.rename_tab(idx))
            menu.addAction(f"💾 Save Note", lambda idx=target_index: self.save_note_as_txt(idx))
            
        menu.addAction("➕ Add New Note Tab", self.add_new_tab)
        menu.addAction("📂 Load Note", self.load_note_from_txt)
        
        if self.tabs.count() > 1 and target_index != -1:
            menu.addAction("🗑️ Close Current Tab", lambda idx=target_index: self.close_tab(idx))
            
        menu.addSeparator()

        self.populate_base_actions(menu)

        menu.exec(global_pos)