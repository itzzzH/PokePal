# widgets/weakness.py
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QGroupBox, QSizeGrip, QWidget, QGridLayout
)
from core.base_overlay import BaseOverlay

class WeaknessWidget(BaseOverlay):
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

    def __init__(self, main_app):
        super().__init__("Type Coverage & Weaknesses", main_app)
        self.selected_types = ["Water"]

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        
        container = QFrame()
        container.setStyleSheet("QFrame { background-color: #1A1A20; border-radius: 12px; border: 1px solid #323242; }")
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(10, 10, 10, 10)
        c_layout.setSpacing(8)
        
        header_lbl = QLabel("🛡️ Matchup Calculator")
        header_lbl.setStyleSheet("color: #FFFFFF; font-size: 13px; font-weight: bold; border: none; background: transparent;")
        c_layout.addWidget(header_lbl)

        # Type Selection Box (Rows of 3)
        select_box = QGroupBox("Select Types (Pick up to 2)")
        select_box.setStyleSheet(self._box_style())
        s_layout = QVBoxLayout(select_box)
        s_layout.setContentsMargins(8, 8, 8, 8)
        s_layout.setSpacing(6)

        self.type_buttons = {}
        type_grid = QGridLayout()
        type_grid.setContentsMargins(0, 0, 0, 0)
        type_grid.setSpacing(3)
        
        for i, t in enumerate(self.TYPES):
            btn = QPushButton(t)
            btn.setCheckable(True)
            btn.setFixedHeight(24)
            btn.setStyleSheet(self._btn_style(self.TYPE_COLORS.get(t, "#3B82F6")))
            if t in self.selected_types:
                btn.setChecked(True)
            btn.clicked.connect(lambda _, val=t: self.on_type_clicked(val))
            type_grid.addWidget(btn, i // 3, i % 3)  # Arranged in 3 columns
            self.type_buttons[t] = btn

        s_layout.addLayout(type_grid)
        c_layout.addWidget(select_box)

        # Results Box
        results_box = QGroupBox("Damage Multipliers Breakdown")
        results_box.setStyleSheet(self._box_style())
        r_layout = QVBoxLayout(results_box)
        r_layout.setContentsMargins(8, 8, 8, 8)
        r_layout.setSpacing(6)

        self.weak_layout = self._create_result_section(r_layout, "⚡ Weaknesses (Increased Damage)", "#FF6B6B")
        self.resist_layout = self._create_result_section(r_layout, "🛡️ Resistances (Reduced Damage)", "#55FF55")
        self.immune_layout = self._create_result_section(r_layout, "🚫 Immunities (Zero Damage)", "#90CDF4")
        
        c_layout.addWidget(results_box, 1)
        layout.addWidget(container)

        if "weakness_pos" in self.main_app.config:
            self.move(*self.main_app.config["weakness_pos"])
        if "weakness_size" in self.main_app.config:
            self.resize(*self.main_app.config["weakness_size"])
        else:
            self.resize(360, 560)

        self.size_grip = QSizeGrip(self)
        self.size_grip.setStyleSheet("background: transparent; width: 14px; height: 14px;")
        self.calculate_matchups()

    def _box_style(self):
        return """
            QGroupBox { color: #A0A0B0; font-size: 11px; font-weight: bold; border: 1px solid #323242; border-radius: 8px; margin-top: 6px; padding-top: 10px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
        """

    def _btn_style(self, color):
        return f"""
            QPushButton {{ background-color: #22222E; color: #C0C0D0; border: 1px solid #3E3E50; border-radius: 4px; font-size: 9px; font-weight: bold; }}
            QPushButton:checked {{ background-color: {color}; color: #FFFFFF; font-weight: bold; border: 1px solid #FFFFFF; }}
            QPushButton:hover {{ background-color: #2D2D3B; border-color: {color}; }}
        """

    def _create_result_section(self, parent_layout, title_text, title_color):
        v_box = QVBoxLayout()
        v_box.setContentsMargins(0, 0, 0, 0)
        v_box.setSpacing(2)
        
        title = QLabel(title_text)
        title.setStyleSheet(f"color: {title_color}; font-size: 10px; font-weight: bold; border: none; background: transparent;")
        v_box.addWidget(title)
        
        rows_container = QWidget()
        rows_layout = QVBoxLayout(rows_container)
        rows_layout.setContentsMargins(0, 0, 0, 0)
        rows_layout.setSpacing(2)
        v_box.addWidget(rows_container)
        
        parent_layout.addLayout(v_box)
        return rows_layout

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.size_grip.move(self.width() - 20, self.height() - 20)

    def on_type_clicked(self, val):
        if val in self.selected_types:
            self.selected_types.remove(val)
        else:
            if len(self.selected_types) >= 2:
                self.selected_types.pop(0)
            self.selected_types.append(val)
        for t, btn in self.type_buttons.items():
            btn.setChecked(t in self.selected_types)
        self.calculate_matchups()

    def populate_section(self, layout, badges_data):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                sub_l = item.layout()
                while sub_l.count():
                    sub_item = sub_l.takeAt(0)
                    if sub_item.widget():
                        sub_item.widget().deleteLater()
                sub_l.deleteLater()
        
        if not badges_data:
            lbl = QLabel("None")
            lbl.setStyleSheet("color: #777788; font-size: 10px; font-style: italic; border: none; background: transparent;")
            layout.addWidget(lbl)
            return

        # Chunk badges into rows of maximum 5
        for i in range(0, len(badges_data), 5):
            chunk = badges_data[i:i+5]
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(4)
            row_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            
            for type_name, mult_str in chunk:
                bg = self.TYPE_COLORS.get(type_name, "#555566")
                badge = QLabel(f"{type_name} ({mult_str})")
                badge.setStyleSheet(f"background-color: {bg}; color: #FFFFFF; font-size: 9px; font-weight: bold; padding: 2px 6px; border-radius: 4px; border: 1px solid rgba(255, 255, 255, 0.3);")
                row_layout.addWidget(badge)
            
            layout.addWidget(row_widget)

    def calculate_matchups(self):
        multipliers = {}
        for dt in self.TYPES:
            mult = 1.0
            for atk_t, defs in self.CHART.items():
                if atk_t == dt:
                    for t in self.selected_types:
                        if t in defs:
                            mult *= defs[t]
            multipliers[dt] = mult

        weak_badges = []
        resist_badges = []
        immune_badges = []

        for dt, mult in multipliers.items():
            if mult == 0.0:
                immune_badges.append((dt, "0x"))
            elif mult > 1.0:
                mult_str = f"{int(mult)}x" if mult.is_integer() else f"{mult}x"
                weak_badges.append((dt, mult_str))
            elif mult < 1.0:
                frac_str = "1/4x" if mult == 0.25 else "1/2x"
                resist_badges.append((dt, frac_str))

        self.populate_section(self.weak_layout, weak_badges)
        self.populate_section(self.resist_layout, resist_badges)
        self.populate_section(self.immune_layout, immune_badges)