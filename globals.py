# globals.py

MODERN_DARK_STYLESHEET = """
QWidget {
    background-color: #121215;
    color: #E2E2E8;
    font-family: 'Segoe UI', sans-serif;
    font-size: 12px;
}
QTabWidget::pane {
    border: 1px solid #2D2D36;
    background: #18181C;
    border-radius: 6px;
}
QTabBar::tab {
    background: #1E1E24;
    color: #A0A0B0;
    padding: 8px 18px;
    border: 1px solid #2D2D36;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background: #2A2A34;
    color: #FFFFFF;
    font-weight: bold;
    border-color: #444452;
}
QGroupBox {
    font-weight: bold;
    color: #D0D0DC;
    border: 1px solid #2D2D36;
    border-radius: 8px;
    margin-top: 8px;
    padding-top: 14px;
    background-color: #18181C;
}
QLineEdit, QComboBox {
    background-color: #22222A;
    border: 1px solid #363644;
    border-radius: 4px;
    color: #FFFFFF;
    padding: 4px 8px;
    font-size: 12px;
}
QComboBox QAbstractItemView {
    background-color: #1A1A20;
    color: #E2E2E8;
    selection-background-color: #323240;
    selection-color: #FFFFFF;
    border: 1px solid #363644;
}
QLineEdit:focus, QComboBox:focus {
    border: 1px solid #5A5A6E;
}
QPushButton {
    background-color: #2A2A34;
    color: #E2E2E8;
    border: 1px solid #3D3D4C;
    border-radius: 5px;
    padding: 5px 10px;
    font-size: 12px;
}
QPushButton:hover {
    background-color: #363644;
    border-color: #5A5A6E;
}
QPushButton:pressed {
    background-color: #1E1E26;
}
QPushButton:checked {
    background-color: #3A3A4B;
    border: 1px solid #80A0FF;
    color: #FFFFFF;
    font-weight: bold;
}
QProgressBar {
    background-color: #22222A;
    border: 1px solid #363644;
    border-radius: 4px;
    text-align: center;
    color: #FFFFFF;
    min-height: 10px;
    max-height: 14px;
    font-size: 10px;
}
QProgressBar::chunk {
    background-color: #80A0FF;
    border-radius: 3px;
}
QSlider::groove:horizontal {
    border: 1px solid #2A2A34;
    height: 6px;
    background: #22222A;
    border-radius: 3px;
}
QSlider::sub-page:horizontal {
    background: #4A4A5B;
    border-radius: 3px;
}
QSlider::add-page:horizontal {
    background: #22222A;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #626276;
    border: 1px solid #808096;
    width: 14px;
    margin-top: -5px;
    margin-bottom: -5px;
    border-radius: 7px;
}
QScrollArea {
    border: none;
    background-color: transparent;
}
QScrollBar:vertical, QScrollBar:horizontal {
    border: none;
    background: #18181C;
    width: 8px;
    height: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
    background: #363644;
    min-height: 20px;
    min-width: 20px;
    border-radius: 4px;
}
QMenu {
    background-color: #1A1A20;
    color: #E2E2E8;
    border: 1px solid #333340;
    border-radius: 6px;
    padding: 4px;
}
QMenu::item {
    padding: 6px 20px 6px 10px;
    border-radius: 4px;
}
QMenu::item:selected {
    background-color: #323240;
    color: #FFFFFF;
}
"""

NATURES_LIST = [
    "Hardy", "Lonely", "Brave", "Adamant", "Naughty",
    "Bold", "Docile", "Relaxed", "Impish", "Lax",
    "Timid", "Hasty", "Serious", "Jolly", "Naive",
    "Modest", "Mild", "Quiet", "Bashful", "Rash",
    "Calm", "Gentle", "Sassy", "Careful", "Quirky"
]

BREEDING_ITEMS = [
    "None", "Everstone", "Power Weight (HP)", "Power Bracer (Atk)", 
    "Power Belt (Def)", "Power Lens (SpA)", "Power Band (SpD)", "Power Anklet (Spe)"
]