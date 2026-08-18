# widgets/weakness.py
import os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPixmapCache
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QGroupBox, QSizeGrip, QWidget, QGridLayout,
    QLineEdit, QCompleter
)
from core.base_overlay import BaseOverlay
import data_manager


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
        self.current_pokemon_name = "Custom Type Selection"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        
        container = QFrame()
        container.setStyleSheet("QFrame { background-color: #141418; border-radius: 10px; border: 1px solid #2A2A38; }")
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(8, 8, 8, 8)
        c_layout.setSpacing(6)
        
        # Header Row
        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)
        
        header_lbl = QLabel("🛡️ Matchup Calculator")
        header_lbl.setStyleSheet("color: #FFFFFF; font-size: 12px; font-weight: bold; border: none; background: transparent;")
        header_row.addWidget(header_lbl)
        header_row.addStretch()
        
        c_layout.addLayout(header_row)

        # Search Bar Row
        search_row = QHBoxLayout()
        search_row.setSpacing(4)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search Pokémon (Name or #ID)...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #1E1E26;
                color: #FFFFFF;
                border: 1px solid #333342;
                border-radius: 5px;
                padding: 4px 8px;
                font-size: 11px;
            }
            QLineEdit:focus { border-color: #3B82F6; }
        """)
        if data_manager.POKEMON_NAMES_LIST:
            completer = QCompleter(data_manager.POKEMON_NAMES_LIST, self.search_input)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
            self.search_input.setCompleter(completer)
            
        self.search_input.returnPressed.connect(self.perform_search)
        
        btn_search = QPushButton("Find")
        btn_search.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: #FFFFFF;
                border: none;
                border-radius: 5px;
                padding: 4px 10px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover { background-color: #2563EB; }
        """)
        btn_search.clicked.connect(self.perform_search)
        
        search_row.addWidget(self.search_input, 1)
        search_row.addWidget(btn_search)
        c_layout.addLayout(search_row)

        # Active Pokémon Modern Banner Card
        self.info_card = QFrame()
        self.info_card.setStyleSheet("QFrame { background-color: #1A1A22; border-radius: 8px; border: 1px solid #2D2D3D; }")
        info_layout = QHBoxLayout(self.info_card)
        info_layout.setContentsMargins(8, 6, 8, 6)
        info_layout.setSpacing(8)

        self.sprite_lbl = QLabel()
        self.sprite_lbl.setFixedSize(40, 40)
        self.sprite_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sprite_lbl.setStyleSheet("background: #141418; border: 1px solid #262633; border-radius: 6px;")
        self.sprite_lbl.setText("❓")
        info_layout.addWidget(self.sprite_lbl)

        info_text_layout = QVBoxLayout()
        info_text_layout.setContentsMargins(0, 0, 0, 0)
        info_text_layout.setSpacing(2)

        self.title_name_lbl = QLabel(self.current_pokemon_name)
        self.title_name_lbl.setStyleSheet("color: #E2E8F0; font-size: 11px; font-weight: bold; border: none; background: transparent;")
        info_text_layout.addWidget(self.title_name_lbl)

        # Container for active type pills inside the banner
        self.active_types_widget = QWidget()
        self.active_types_layout = QHBoxLayout(self.active_types_widget)
        self.active_types_layout.setContentsMargins(0, 0, 0, 0)
        self.active_types_layout.setSpacing(4)
        self.active_types_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        info_text_layout.addWidget(self.active_types_widget)

        info_layout.addLayout(info_text_layout, 1)
        c_layout.addWidget(self.info_card)

        # Compact Type Selection Grid Box
        select_box = QGroupBox("Select Types (Max 2)")
        select_box.setStyleSheet(self._box_style())
        s_layout = QVBoxLayout(select_box)
        s_layout.setContentsMargins(6, 6, 6, 6)
        s_layout.setSpacing(4)

        self.type_buttons = {}
        type_grid = QGridLayout()
        type_grid.setContentsMargins(0, 0, 0, 0)
        type_grid.setSpacing(3)
        
        for i, t in enumerate(self.TYPES):
            btn = QPushButton(t)
            btn.setCheckable(True)
            btn.setFixedHeight(22)
            btn.setStyleSheet(self._btn_style(self.TYPE_COLORS.get(t, "#3B82F6")))
            if t in self.selected_types:
                btn.setChecked(True)
            btn.clicked.connect(lambda _, val=t: self.on_type_clicked(val))
            type_grid.addWidget(btn, i // 3, i % 3)
            self.type_buttons[t] = btn

        s_layout.addLayout(type_grid)
        c_layout.addWidget(select_box)

        # Results Box
        results_box = QGroupBox("Damage Multipliers Breakdown")
        results_box.setStyleSheet(self._box_style())
        r_layout = QVBoxLayout(results_box)
        r_layout.setContentsMargins(6, 6, 6, 6)
        r_layout.setSpacing(4)

        self.weak_layout = self._create_result_section(r_layout, "⚡ Weaknesses", "#FF6B6B")
        self.resist_layout = self._create_result_section(r_layout, "🛡️ Resistances", "#55FF55")
        self.immune_layout = self._create_result_section(r_layout, "🚫 Immunities", "#90CDF4")
        
        c_layout.addWidget(results_box, 1)
        layout.addWidget(container)

        if "weakness_pos" in self.main_app.config:
            self.move(*self.main_app.config["weakness_pos"])
        if "weakness_size" in self.main_app.config:
            self.resize(*self.main_app.config["weakness_size"])
        else:
            self.resize(340, 570)

        self.size_grip = QSizeGrip(self)
        self.size_grip.setStyleSheet("background: transparent; width: 14px; height: 14px;")
        self.update_header_info()
        self.calculate_matchups()

    @staticmethod
    def _box_style():
        return """
            QGroupBox { color: #8F8FA8; font-size: 10px; font-weight: bold; border: 1px solid #282836; border-radius: 6px; margin-top: 4px; padding-top: 8px; }
            QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 3px; }
        """

    @staticmethod
    def _btn_style(color):
        return f"""
            QPushButton {{ background-color: #1B1B24; color: #A0A0B2; border: 1px solid #2E2E3D; border-radius: 4px; font-size: 9px; font-weight: bold; }}
            QPushButton:checked {{ background-color: {color}; color: #FFFFFF; font-weight: bold; border: 1px solid #FFFFFF; }}
            QPushButton:hover {{ background-color: #262633; border-color: {color}; }}
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
        rows_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        v_box.addWidget(rows_container)
        
        parent_layout.addLayout(v_box)
        return rows_layout

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.size_grip.move(self.width() - 20, self.height() - 20)

    def load_sprite(self, cid):
        cache_key = f"weakness_sprite_{cid}"
        pix = QPixmapCache.find(cache_key)

        if pix is None:
            paths = [
                os.path.join("data", "sprites", f"{cid}.png"),
                os.path.join("sprites", f"{cid}.png"),
                f"{cid}.png"
            ]
            for p in paths:
                if os.path.exists(p):
                    loaded_pix = QPixmap(p)
                    if not loaded_pix.isNull():
                        pix = loaded_pix.scaled(36, 36, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                        QPixmapCache.insert(cache_key, pix)
                    break

        if pix and not pix.isNull():
            self.sprite_lbl.setPixmap(pix)
            self.sprite_lbl.setText("")
        else:
            self.sprite_lbl.clear()
            self.sprite_lbl.setText("❓")

    def update_header_info(self):
        self.title_name_lbl.setText(self.current_pokemon_name)
        
        # Clear active types pills in banner
        while self.active_types_layout.count():
            item = self.active_types_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        for t in self.selected_types:
            bg = self.TYPE_COLORS.get(t, "#444455")
            badge = QLabel(t)
            badge.setFixedHeight(18)
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            badge.setStyleSheet(
                f"background-color: {bg}; color: #FFFFFF; font-size: 9px; font-weight: bold; "
                f"padding: 1px 6px; border-radius: 4px; border: none;"
            )
            self.active_types_layout.addWidget(badge)

    def perform_search(self):
        txt = self.search_input.text().strip()
        if not txt:
            return
        if txt.startswith("#"):
            txt = txt[1:]
        parts = txt.split(" ")
        query_val = parts[0].lower()
        
        entry = None
        if query_val.isdigit():
            entry = data_manager.MASTER_DEX_DB.get(query_val)
        else:
            entry = data_manager.MASTER_DEX_DB.get(query_val)
            
        if entry:
            self.current_pokemon_name = entry.get("name", "Unknown Pokémon").capitalize()
            cid = entry.get("_clean_id")
            if cid:
                self.load_sprite(cid)
            types = entry.get("types", [])
            cleaned_types = [str(t).capitalize() for t in types if str(t).capitalize() in self.TYPES]
            if cleaned_types:
                self.selected_types = cleaned_types[:2]
                for t, btn in self.type_buttons.items():
                    btn.setChecked(t in self.selected_types)
                self.update_header_info()
                self.calculate_matchups()

    def on_type_clicked(self, val):
        if val in self.selected_types:
            self.selected_types.remove(val)
        else:
            if len(self.selected_types) >= 2:
                self.selected_types.pop(0)
            self.selected_types.append(val)
        for t, btn in self.type_buttons.items():
            btn.setChecked(t in self.selected_types)
        
        self.current_pokemon_name = "Custom Type Selection"
        self.sprite_lbl.clear()
        self.sprite_lbl.setText("⚙️")
        self.update_header_info()
        self.calculate_matchups()

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
                item.layout().deleteLater()

    def populate_section(self, layout, badges_data):
        self._clear_layout(layout)
        
        if not badges_data:
            lbl = QLabel("None")
            lbl.setStyleSheet("color: #666677; font-size: 9px; font-style: italic; border: none; background: transparent;")
            lbl.setFixedHeight(20)
            lbl.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            layout.addWidget(lbl)
            return

        for i in range(0, len(badges_data), 5):
            chunk = badges_data[i:i+5]
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(3)
            row_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            
            for type_name, mult_str in chunk:
                bg = self.TYPE_COLORS.get(type_name, "#555566")
                badge = QLabel(f"{type_name} ({mult_str})")
                badge.setFixedHeight(20)
                badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
                badge.setStyleSheet(
                    f"background-color: {bg}; color: #FFFFFF; font-size: 9px; font-weight: bold; "
                    f"padding: 1px 6px; border-radius: 4px; border: 1px solid rgba(255, 255, 255, 0.2);"
                )
                row_layout.addWidget(badge)
            
            layout.addWidget(row_widget)

    def calculate_matchups(self):
        multipliers = {}
        for atk_type in self.TYPES:
            mult = 1.0
            type_chart = self.CHART.get(atk_type, {})
            for def_type in self.selected_types:
                if def_type in type_chart:
                    mult *= type_chart[def_type]
            multipliers[atk_type] = mult

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