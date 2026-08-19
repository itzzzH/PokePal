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

TYPES = [
    "Normal", "Fire", "Water", "Grass", "Electric", "Ice", 
    "Fighting", "Poison", "Ground", "Flying", "Psychic", "Bug", 
    "Rock", "Ghost", "Dragon", "Dark", "Steel", "Fairy"
]

TYPE_COLORS = {
    "Normal": "#95956C", "Fire": "#FF9933", "Water": "#3399FF", 
    "Grass": "#33CC33", "Electric": "#FFCC00", "Ice": "#66CCFF", 
    "Fighting": "#CC3300", "Poison": "#9933CC", "Ground": "#CC9933", 
    "Flying": "#6699CC", "Psychic": "#FF3399", "Bug": "#A6B91A", 
    "Rock": "#B8A038", "Ghost": "#705898", "Dragon": "#7038F8", 
    "Dark": "#705848", "Steel": "#B8B8D0", "Fairy": "#EE99AC"
}

CHART = {
    "Normal": {"Rock": 0.5, "Ghost": 0.0, "Steel": 0.5},
    "Fire": {"Fire": 0.5, "Water": 0.5, "Grass": 2.0, "Ice": 2.0, "Bug": 2.0, "Rock": 0.5, "Dragon": 0.5, "Steel": 2.0},
    "Water": {"Fire": 2.0, "Water": 0.5, "Grass": 0.5, "Ground": 2.0, "Rock": 2.0, "Dragon": 0.5},
    "Grass": {"Fire": 0.5, "Water": 2.0, "Grass": 0.5, "Poison": 0.5, "Ground": 2.0, "Flying": 0.5, "Bug": 0.5, "Rock": 2.0, "Dragon": 0.5, "Steel": 0.5},
    "Electric": {"Water": 2.0, "Grass": 0.5, "Electric": 0.5, "Ground": 0.0, "Flying": 2.0, "Dragon": 0.5},
    "Ice": {"Fire": 0.5, "Water": 0.5, "Grass": 2.0, "Ground": 2.0, "Flying": 2.0, "Dragon": 2.0, "Steel": 0.5, "Ice": 0.5},
    "Fighting": {"Normal": 2.0, "Ice": 2.0, "Poison": 0.5, "Flying": 0.5, "Psychic": 0.5, "Bug": 0.5, "Rock": 2.0, "Ghost": 0.0, "Dark": 2.0, "Steel": 2.0, "Fairy": 0.5},
    "Poison": {"Grass": 2.0, "Poison": 0.5, "Ground": 0.5, "Rock": 0.5, "Ghost": 0.5, "Steel": 0.0, "Fairy": 2.0},
    "Ground": {"Fire": 2.0, "Grass": 0.5, "Electric": 2.0, "Poison": 2.0, "Flying": 0.0, "Bug": 0.5, "Rock": 2.0, "Steel": 2.0},
    "Flying": {"Grass": 2.0, "Electric": 0.5, "Fighting": 2.0, "Bug": 2.0, "Rock": 0.5, "Steel": 0.5},
    "Psychic": {"Fighting": 2.0, "Poison": 2.0, "Psychic": 0.5, "Dark": 0.0, "Steel": 0.5},
    "Bug": {"Fire": 0.5, "Grass": 2.0, "Fighting": 0.5, "Poison": 0.5, "Flying": 0.5, "Psychic": 2.0, "Ghost": 0.5, "Dark": 2.0, "Steel": 0.5, "Fairy": 0.5},
    "Rock": {"Fire": 2.0, "Ice": 2.0, "Fighting": 0.5, "Ground": 0.5, "Flying": 2.0, "Bug": 2.0, "Steel": 0.5},
    "Ghost": {"Normal": 0.0, "Psychic": 2.0, "Ghost": 2.0, "Dark": 0.5},
    "Dragon": {"Dragon": 2.0, "Steel": 0.5, "Fairy": 0.0},
    "Dark": {"Fighting": 0.5, "Psychic": 2.0, "Ghost": 2.0, "Dark": 0.5, "Fairy": 0.5},
    "Steel": {"Fire": 0.5, "Water": 0.5, "Electric": 0.5, "Ice": 2.0, "Rock": 2.0, "Steel": 0.5, "Fairy": 2.0},
    "Fairy": {"Fire": 0.5, "Fighting": 2.0, "Poison": 0.5, "Dragon": 2.0, "Dark": 2.0, "Steel": 0.5}
}